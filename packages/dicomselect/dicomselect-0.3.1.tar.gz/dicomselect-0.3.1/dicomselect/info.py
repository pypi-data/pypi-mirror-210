from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from dicomselect.query import Query


class Info:
    def __init__(self, parent: 'Query', rows: List[tuple], cols: Dict[str, Dict[str, int]]):
        self._query_parent = parent
        self._rows = rows
        self._cols = cols

    @property
    def count(self) -> int:
        return len(self._rows)

    def query(self) -> 'Query':
        return self._query_parent

    def print(self, sort_by_homogeneous: bool = True) -> 'Info':
        """
        Print the current results of a query

        Parameters
        ----------
        sort_by_homogeneous: bool (default: True)
            Sort by homogeneous columns.
        """
        sort_by_similarity = sorted(
            sorted(self._cols.keys()),
            key=lambda k: len(self._cols[k]),
            reverse=not sort_by_homogeneous
        )

        header = f'Total selected DICOMs: {self.count}'
        print(header)
        print('=' * len(header))
        for key in sort_by_similarity:
            print(key)
            items = sorted(self._cols[key].items(), key=lambda a: a[1], reverse=True)
            for value, count in items:
                count: str = f'({count})'.ljust(len(str(len(self._rows))) + 2)
                print(f'\t{count} {value}')

        return self

    def filter(self, *columns: str) -> 'Info':
        filtered_cols = {key: value for key, value in self._cols.items() if key in columns}
        return Info(self._query_parent, self._rows, filtered_cols)
