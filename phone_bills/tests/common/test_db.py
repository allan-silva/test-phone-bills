import pytest
from datetime import datetime


@pytest.fixture
def condition_entry():
    return dict(start_date=datetime.now(), end_date=datetime.now())


def test_tables_defined(dbo):
    assert dbo.tariff_conditions


def test_insert_condition(dbo, condition_entry):
    start_date = condition_entry['start_date']
    end_date = condition_entry['end_date']
    ret = dbo.tariff_conditions.insert(**condition_entry)
    assert 'id' in ret and ret['id']
    assert ret['start_date'] == start_date
    assert ret['end_date'] == end_date
    rows = dbo.tariff_conditions.select()
    assert len(rows) == 1
