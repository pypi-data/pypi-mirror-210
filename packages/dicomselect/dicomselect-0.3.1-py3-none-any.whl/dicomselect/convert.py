import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import SimpleITK as sitk
from tqdm import tqdm
from treelib import Tree

from dicomselect.reader import DICOMImageReader


class Mutation(Enum):
    OVERWRITE = '~'
    NEW = '+'
    REMOVE = '-'
    MISSING = '!'


def load_plan(path: os.PathLike) -> "Plan":
    """Load a conversion plan from a json file."""
    path = Path(path)
    if path.is_dir():
        path = path / 'dicomselect_conversion_plan.json'

    with open(path, 'r') as f:
        plan_json = json.load(f)

    converts = [Convert(**json.loads(c), columns=[], values=[]) for c in plan_json['_converts']]
    plan = Plan(plan_json['source_dir'], converts)
    plan.target_dir = plan_json['target_dir']
    plan.extension = plan_json['suffix']
    plan.overwrite_existing = plan_json['overwrite_existing']
    plan.remove_existing = plan_json['remove_existing']

    return plan


class Convert:
    def __init__(self, uid: str, source: str, target: str, columns: List[str], values: List[str]):
        if len(columns) != len(values):
            raise RuntimeError()

        self.uid = uid
        self.source = Path(source)
        for col, value in {columns[i]: values[i] for i in range(len(columns))}.items():
            target = self._column_replace_sanitize(target, col, value)
        self.target = Path(target)

    # noinspection RegExpRedundantEscape
    @staticmethod
    def _column_replace_sanitize(text: str, col: str, value):
        placeholder = '{' + col + '}'
        value = str(value)
        # no non-printable characters
        value = re.sub(r'[\x00-\x1F]', '', value)
        # forbidden ascii characters
        value = re.sub(r'[<>:"\/\\\|\?\*]', '#', value)
        # may not end with a dot or space
        value = re.sub(r'[\. ]+$', '', value)
        # if the result is empty, return [col]=blank instead
        if len(value) == 0:
            return f'{col}=blank'
        return text.replace(placeholder, value)

    def __repr__(self):
        return f'{self.source} -> {self.target}'

    def convert(self, suffix: str, source_dir: Path, target_dir: Path, postprocess_func):
        reader = DICOMImageReader(source_dir / self.source)

        image = reader.image
        if postprocess_func:
            image = postprocess_func(image)

        target = (target_dir / self.target).with_suffix(suffix)
        target.parent.mkdir(exist_ok=True)
        target_tmp = target.with_name(f"tmp_{target.name}")
        sitk.WriteImage(image, target_tmp.as_posix(), useCompression=True)
        os.replace(target_tmp, target)

        # for .dicomselect
        return f'{self.uid}\t{target.relative_to(target_dir)}'


class Plan:
    def __init__(self, default_source_dir: Path, converts: List[Convert]):
        self._converts = converts

        self._remove_existing: bool = False
        self._overwrite_existing: bool = False
        self._source_dir = default_source_dir
        self._extension = '.mha'
        self._target_dir: Path = None

        self._missing: List[Path] = []
        self._mutation: Dict[str, Tuple[Mutation, Convert]] = dict()
        self._invalidated = True

    def _invalidate(self, attr: str, value):
        if getattr(self, attr) != value:
            self._invalidated = True

    @property
    def source_dir(self) -> Path:
        """
        Source directory, containing your data that is to be converted.
        """
        return self._source_dir

    @source_dir.setter
    def source_dir(self, value: os.PathLike):
        value = Path(value).absolute()
        assert value.exists(), NotADirectoryError(f'{value} does not exist.')
        assert value.is_dir(), NotADirectoryError(f'{value} is not a directory.')
        self._invalidate('source_dir', value)
        self._source_dir = value

    @property
    def target_dir(self) -> Path:
        """
        Target directory, to contain the converted data.
        """
        return self._target_dir

    @target_dir.setter
    def target_dir(self, value: os.PathLike):
        value = Path(value).absolute()
        assert value is not None, ValueError('target_dir is not set.')
        assert not value.exists() or value.is_dir(), NotADirectoryError(f'{value} is not a directory.')
        self._invalidate('target_dir', value)
        self._target_dir = value

    @property
    def extension(self) -> str:
        """
        The suffix defines the converted filetype. See https://simpleitk.readthedocs.io/en/master/IO.html#images
        for possible file formats to convert to.
        """
        return self._extension

    @extension.setter
    def extension(self, value: str):
        assert value.startswith('.'), ValueError('extension must start with a period.')
        self._invalidate('extension', value)
        self._extension = value

    @property
    def remove_existing(self) -> bool:
        """
        Whether to remove any existing files in target_dir.
        """
        return self._remove_existing

    @remove_existing.setter
    def remove_existing(self, value: bool):
        self._invalidate('remove_existing', value)
        self._remove_existing = value

    @property
    def overwrite_existing(self) -> bool:
        """
        Whether to overwrite any existing files in target_dir that are the same.
        Files are considered the same if they share the same database key value and file name.
        """
        return self._overwrite_existing

    @overwrite_existing.setter
    def overwrite_existing(self, value: bool):
        self._invalidate('overwrite_existing', value)
        self._overwrite_existing = value

    def _update_mutations(self):
        if not self._invalidated:
            return

        self.source_dir = self._source_dir  # performs a validation of source dir
        self.target_dir = self._target_dir  # performs a validation of target dir

        _dicomselect = self.target_dir / '.dicomselect'
        _dicomselect_dict = dict()
        try:
            if _dicomselect.exists():
                with open(_dicomselect, 'r') as fp:
                    for line in fp.readlines():
                        # column 1 is the file name, column 2 is the uid
                        line_expected = re.search(r'([0-9a-f]+)\t(.+)', line)
                        if line_expected:
                            _dicomselect_dict[line_expected.group(1)] = Path(line_expected.group(2))
                        else:
                            raise
        except:
            print('.dicomselect file appears corrupt; overwrite_existing is forcibly set to True')
            self.overwrite_existing = True
            _dicomselect_dict.clear()

        self._mutation.clear()
        self._missing.clear()
        for convert in tqdm(self._converts, desc=f"Preparing conversion plan"):
            source_exists = (self.source_dir / convert.source).exists()
            target_exists = (self.target_dir / convert.target).with_suffix(self.extension).exists()
            if target_exists and convert.uid in _dicomselect_dict:
                mutation_key = _dicomselect_dict[convert.uid].as_posix()
                self._mutation[mutation_key] = (Mutation.OVERWRITE, convert)
            else:
                i = 0
                while True:
                    target = f'{convert.target}_{i}{self.extension}'
                    if target not in self._mutation:
                        break
                    i += 1
                mutation_key = Path(target).as_posix()
                self._mutation[mutation_key] = (Mutation.NEW, convert)
            if not source_exists:
                self._mutation[mutation_key] = (Mutation.MISSING, None)
                self._missing.append(mutation_key)

        if self.remove_existing:
            # gather a list of files in target_dir that are not in the conversion plan
            print(f"Checking existing files in {self.target_dir}...")
            for root, directories, files in tqdm(os.walk(self.target_dir), desc=f"Checking existing files"):
                for fn in files:
                    filepath = (Path(root) / fn).relative_to(self.target_dir)
                    if filepath not in self._mutation and filepath.name != _dicomselect.name:
                        self._mutation[filepath.as_posix()] = (Mutation.REMOVE, None)

        mutation_list = list(self._mutation.items())
        for path, (mut, _) in mutation_list:
            del_overwrite = not self.overwrite_existing and mut == Mutation.OVERWRITE
            del_remove = not self.remove_existing and mut == Mutation.REMOVE
            if del_overwrite or del_remove:
                self._mutation.pop(path)

        self._invalidated = False

    def _tree(self) -> Tree:
        self._update_mutations()

        tree = Tree()
        root = tree.create_node('.', Path('.'))
        for path, (mut, _) in self._mutation.items():
            prev_parent = root
            path = Path(path)
            for parent in path.parents:
                if parent not in tree:
                    tree.create_node(str(parent), parent, parent=prev_parent.identifier)
            tree.create_node(f'({mut.value}) {path.name}', path, parent=path.parent)

        return tree

    def _parameters(self) -> dict:
        parameters = ['source_dir', 'target_dir', 'suffix', 'overwrite_existing', 'remove_existing']
        return {key: self._serialize(getattr(self, key)) for key in parameters}

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, Convert):
            return json.dumps(obj.__dict__, default=Plan._serialize)
        if isinstance(obj, Path):
            return obj.as_posix()
        return obj

    def print(self) -> str:
        """
        Prints the conversion plan as a string, in a tree representation.

        Returns
        -------
        The printout as a str.
        """
        self._update_mutations()

        tree = self._tree()
        text = 'dicomselect conversion plan\n\n'
        text += '\n'.join([f'{name:<20}{value}' for name, value in self._parameters().items()])
        if len(self._missing) > 0:
            text += f'{len(self._missing)} files not found in {self.source_dir}!'
            text += '\n\t'.join([f'! {str(m)}' for m in self._missing])

        text += '\n' + tree.show(stdout=False)
        print(text)
        return text

    def save_as(self, path: os.PathLike) -> str:
        """Save the conversion plan to a file."""
        self._update_mutations()

        path = Path(path)
        if path.is_dir():
            path = path / 'dicomselect_conversion_plan.json'

        plan = json.dumps({**self._parameters(), '_converts': self._converts}, default=self._serialize, indent=2)
        with open(path, 'w') as f:
            f.write(plan)

    def execute(self, max_workers: int = 4, postprocess_func: Optional[Callable[[sitk.Image], sitk.Image]] = None):
        """
        Execute the conversion plan.

        Parameters
        ----------
        max_workers: int
            Max workers for the parallel process.
        postprocess_func:
            Postprocess function which takes a SimpleITK.Image and expects an output SimpleITK.Image, just prior to conversion.
        """
        self._update_mutations()
        errors = []
        _dicomselect = []
        convert_args = (self.extension, self.source_dir, self.target_dir, postprocess_func)

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True)

        def _execute(path: Path, mutation: Mutation, convert: Convert) -> Union[str, None]:
            if convert:
                return convert.convert(*convert_args)
            elif mutation == Mutation.REMOVE:
                os.remove(self.target_dir / path)

        print(f"Converting {len(self._converts)} DICOM series from {self.source_dir} to {self.target_dir}")
        with tqdm(total=len(self._converts), desc=f"Converting to {self.extension}") as pbar, ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(_execute, path, mut, convert) for path, (mut, convert) in self._mutation.items()]
            for future in as_completed(futures):
                _dicomselect.append(future.result())
                errors.append(future.exception())
                pbar.update()

        with open(self.target_dir / '.dicomselect', 'w') as f:
            f.write('\n'.join([item for item in _dicomselect if item]))

        print(f"Completed conversion with {len(errors)} errors.")
        print(self._format_errors(errors))

    @staticmethod
    def _format_errors(errors):
        return "\t" + "\n\t".join([str(e) for e in errors if e])
