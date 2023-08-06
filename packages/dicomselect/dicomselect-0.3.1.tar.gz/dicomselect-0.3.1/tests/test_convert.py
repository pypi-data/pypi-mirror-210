import shutil
from pathlib import Path

import pytest

from dicomselect import Database, load_plan


def test_plan():
    output = Path('tests/output')
    output_expected = Path('tests/output_expected')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()

    db = Database(output_expected / 'test.db')
    with db as query:
        query_0000 = query.where('patient_id', '=', 'ProstateX-0000')
        query_0001 = query.where('patient_id', '=', 'ProstateX-0001')

    plan = db.plan('{patient_id}/prostateX_{protocol_name}_{acquisition_date}', query_0000, query_0001)
    plan.target_dir = output / 'convert'
    plan.overwrite_existing = True
    plan.print()
    plan.save_as(output)
    plan_loaded = load_plan(output)
    plan_loaded.save_as(output / 'dicomselect_conversion_plan_loaded')

    plan_json_expected = output_expected / 'dicomselect_conversion_plan.json'
    plan_json_1 = output / 'dicomselect_conversion_plan.json'
    plan_json_2 = output / 'dicomselect_conversion_plan_loaded.json'
    with open(plan_json_expected, 'rb') as f1, open(plan_json_1, 'rb') as f2, open(plan_json_2, 'rb') as f3:
        while True:
            byte1 = f1.read(1)
            byte2 = f2.read(1)
            byte3 = f3.read(1)
            if byte1 != byte2 or byte1 != byte3:
                raise AssertionError("Files are not equal")
            if not byte1:
                break

    plan.execute(max_workers=1)

    # TODO: confirm ADD behaviour, confirm OVERWRITE behaviour, confirm /convert in output and output_expected are same
