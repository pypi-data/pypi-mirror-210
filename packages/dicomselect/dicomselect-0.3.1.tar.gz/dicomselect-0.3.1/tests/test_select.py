from time import time

import pytest

from dicomselect.database import Database


def test_select_simple():
    db = Database('tests/output_expected/test.db')
    vals = ['75', '80', '97', '100']
    col = 'percent_sampling'

    with db as query:
        def assert_query(operator, values, expected):
            a = query.where(col, operator, values)
            assert a.count == expected
            a = query.where(col, operator, values, invert=True)
            assert a.count == 111 - expected

        with pytest.raises(ValueError):
            assert_query('invalid', vals, 0)
        with pytest.raises(ValueError):
            query.where('invalid-col', '=', vals)

        assert_query('=', vals[0], 11)
        assert_query('=', vals, 111)
        assert_query('>', vals[0], 100)

        assert_query('LIKE', ['75%', '80%'], 17)  # 75 !=
        assert_query('Like', '%7%', 14)

        with pytest.raises(ValueError):
            assert_query('between', vals[0], 0)
        with pytest.raises(ValueError):
            assert_query('between', vals[:3], 0)
        assert_query('betWEEN', vals[:2], 17)
        assert_query('BETween', vals, 111)

        assert_query('in', vals[0], 11)
        assert_query('in', vals, 111)


def test_select_complex():
    db = Database('tests/output_expected/test.db')
    with db as query:
        chained = query.where('percent_sampling', '>', '75').where('percent_sampling', '=', '80')
        assert chained.count == 6

        union = query.where('percent_sampling', '=', '97').union(chained)
        assert union.count == 9

        intersect = query.where('number_of_phase_encoding_steps', '=', '167').intersect(chained)
        assert intersect.count == 3

        diff = query.where('number_of_phase_encoding_steps', '>=', '167').intersect(chained)
        assert diff.count == 3


def test_select_speed():
    db = Database('tests/output_expected/test.db')
    n = 500
    with db as query:
        now = time()
        for _ in range(n):
            query.where('percent_sampling', '=', '97').where('number_of_phase_encoding_steps', '=', '451')
        assert time() - now < 1

        now = time()
        for _ in range(n):
            query.where('percent_sampling', '=', '97')
            query.where('number_of_phase_encoding_steps', '=', '451')
        assert time() - now < 1


def test_select_info(capfd):
    db = Database('tests/output_expected/test.db')
    with db as query:
        paths_info = query.where('patient_id', '=', 'ProstateX-0000').info()
        paths_info.print()
        assert paths_info.count == 7
