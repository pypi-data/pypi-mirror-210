import binascii
import os
import re
import shutil
import sqlite3
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import PathLike
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd
from tqdm import tqdm

from dicomselect.convert import Convert, Plan
from dicomselect.query import Query
from dicomselect.queryfactory import QueryFactory
from dicomselect.reader import DICOMImageReader

database_version = '0.4'


class Database:
    def __init__(self, db_path: PathLike):
        self._db_path = Path(db_path).absolute()
        if self._db_path.is_dir() or self._db_path.suffix != '.db':
            raise IsADirectoryError('Provide a file path with as extension, .db')
        self._errors = []
        self._conn: sqlite3.Connection = None
        self._query_factory: QueryFactory = None
        self._db_dir: Path = None

    @property
    def source_dir(self) -> Path:
        if not self._db_dir:
            try:
                with self:
                    self._db_dir = Path(self._conn.execute('SELECT datadir FROM meta').fetchone()[0])
            except:
                raise sqlite3.DataError(f'No source directory found! Did you create a database at {self._db_path}?')
        return self._db_dir

    @property
    def version(self) -> str:
        if self._db_path.exists():
            cursor = sqlite3.connect(self._db_path, timeout=10)
            return cursor.execute('SELECT version FROM meta').fetchone()[0]
        return database_version

    def __enter__(self) -> Query:
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self) -> Query:
        with open(self._db_path, "rb") as f:
            file_header = binascii.hexlify(f.read(16)).decode("utf-8")
        # official sqlite3 file header
        if not file_header.startswith("53514c69746520666f726d6174203300"):
            sqlite3.DatabaseError(f'{self._db_path} does not appear to be a valid database')

        db_version = database_version.split('.')
        this_db_version = self.version.split('.')
        if db_version[0] != this_db_version[0]:
            raise RuntimeError(f'this database ({this_db_version}) is outdated by a major revision {db_version}')
        if db_version[1] > this_db_version[1]:
            warnings.warn(f'this database ({this_db_version}) is outdated by a minor revision {db_version}')

        self._conn = sqlite3.connect(self._db_path)
        self._query_factory = QueryFactory(self._conn)

        return self._query_factory.create_query(None)

    def close(self):
        self._conn.close()

    def plan(self, filepath_template: str, *queries: Query) -> Plan:
        """
        Prepare a conversion plan, which can convert the results of queries to MHA files.

        Parameters
        ----------
        filepath_template: PathLike
            Dictates the form of the directory and filename structure, omitting the suffix.
            Use braces along with column names to replace with that column value.
            Use forward slash to create a directory structure.
            (see Query.columns for a full list of available columns).
            A unique id will be appended at the end.

            Illegal characters will be replaced with '#'.
            Blank column values will be replaced with '(column_name)=blank'
        queries: Query
            The combined results of the query object will be converted to MHA.

        Returns
        -------
        A conversion plan.
        """
        with self as query:
            cols = query.columns
            requested_cols = [r.group(1) for r in re.finditer(r'{(.+?)}', filepath_template)]
            QueryFactory.check_if_exists('column', cols, *requested_cols)

            ids = set()
            for q in queries:
                ids = ids.union(q._ids)
            self._conn.execute('CREATE TEMPORARY TABLE convert_ids (id INTEGER)')
            self._conn.executemany('INSERT INTO convert_ids (id) VALUES (?)', [(i,) for i in ids])
            converts_fetched = self._conn.execute(
                f'SELECT dicomselect_uid, path, {", ".join(requested_cols)} FROM data JOIN convert_ids ON data.id = convert_ids.id').fetchall()
            converts = [Convert(fetched[0], fetched[1], filepath_template, requested_cols, fetched[2:]) for fetched in converts_fetched]

        return Plan(self.source_dir, converts)

    def create(self, data_dir: PathLike, max_workers: int = 4, *additional_dicom_tags: str):
        """
        Build a database from DICOMs in subdirectories of data_dir.

        Parameters
        ----------
        data_dir: PathLike
            Directory containing .dcm data or dicom.zip data.
        max_workers
            Max number of workers for parallel execution of database creation.
        additional_dicom_tags
            See https://www.dicomlibrary.com/dicom/dicom-tags/, input any additional tags that are not included by default
            Each tag should be formatted as shown in the DICOM tag library, eg. '(0002,0000)'.
        """
        self._errors = []

        data_dir = Path(data_dir).absolute()
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            temp_db = Path(temp_dir) / 'temp.db'
            subdirectories = [data_dir / path for path in os.listdir(data_dir)]

            example_metadata = None
            for subdir in subdirectories:
                try:
                    root, _ = next(self._dicoms_in_dir(subdir))
                    reader = DICOMImageReader(root, allow_raw_tags=False, *additional_dicom_tags)
                    example_metadata = reader.metadata
                    columns = ', '.join(sorted([f'{name} {dtype}' for name, dtype in reader.column_info().items()]))
                    break
                except StopIteration:
                    pass
            if example_metadata is None:
                raise sqlite3.DataError(f'No dicom data found in {data_dir}')

            cursor = sqlite3.connect(temp_db)
            cursor.execute(f'CREATE TABLE data (id INTEGER PRIMARY KEY AUTOINCREMENT, series_length INTEGER, path TEXT, {columns});')
            cursor.close()

            print(f"Creating database from DICOMs subdirectories of {data_dir}.")
            print("Collecting all subdirectories...")

            subdirectories = [data_dir / path for path in os.listdir(data_dir)]
            with tqdm(total=len(subdirectories)) as pbar, ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = [pool.submit(self._thread_execute_dir, temp_db, path.absolute(), additional_dicom_tags) for path in subdirectories]
                for future in as_completed(futures):
                    self._errors.append(future.exception())
                    pbar.update()

            cursor = sqlite3.connect(temp_db, timeout=10)
            df_meta = pd.DataFrame({'datadir': str(data_dir), 'version': database_version}, index=[0])
            df_meta.to_sql(name='meta', con=cursor, if_exists='replace')
            cursor.close()

            if self._db_path.exists():
                os.remove(self._db_path)
            shutil.copy(temp_db, self._db_path)

            self._errors = [err for err in self._errors if err]
            print(f"Database created at {self._db_path} with {len(self._errors)} errors.")
            print(self._format_errors())

    def _format_errors(self):
        return "\t" + "\n\t".join([str(e) for e in self._errors if e])

    def _dicoms_in_dir(self, subdir: Path) -> Tuple[Path, Path]:
        for root, _, filenames in os.walk(subdir, onerror=lambda err: self._errors.append(err)):
            if any([file.endswith('.dcm') for file in filenames]) or 'dicom.zip' in filenames:
                rel_path = Path(root).relative_to(subdir.parent)
                yield root, rel_path

    def _metadata_in_dir(self, subdir: Path, *additional_tags: str):
        for root, rel_path in self._dicoms_in_dir(subdir):
            metadata = dict()
            try:
                reader = DICOMImageReader(root, allow_raw_tags=False, *additional_tags)
                metadata = reader.metadata
                metadata["series_length"] = len(reader.dicom_slice_paths)
                metadata["path"] = str(rel_path)
            except BaseException as e:
                self._errors.append(str(e))
            if metadata:
                yield metadata

    def _thread_execute_dir(self, db: Path, subdir: Path, additional_tags: Dict[str, str]):
        with sqlite3.connect(db, timeout=10, check_same_thread=False) as conn:
            df_rows = pd.DataFrame.from_dict(list(self._metadata_in_dir(subdir, additional_tags)), orient='columns')
            df_rows.to_sql(name='data', con=conn, if_exists='append', index=False)
