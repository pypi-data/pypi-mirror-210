import sqlite3
from pathlib import Path

import pytest

from dicomselect.database import Database


def test_input():
    db_path = Path('tests/output/test.db')
    db_path.parent.mkdir(exist_ok=True)
    db = Database(db_path)
    db.create('tests/input/ProstateX', max_workers=4)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute('SELECT COUNT(*) FROM DATA;').fetchone()[0]
        assert count > 0, f'{db_path} contains no data'
        assert count > 100, f'{db_path} contains an unexpectedly low amount of data'

    with open(db_path, 'rb') as file1, open('tests/output_expected/test.db', 'rb') as file2:
        assert all(a == b for a, b in zip(file1, file2))


def test_input_empty():
    db_path = 'tests/output/test.db'
    db = Database(db_path)

    with pytest.raises(sqlite3.DataError):
        db.create('tests/input/ProstateX-empty')
