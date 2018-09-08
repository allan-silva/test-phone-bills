import pytest

from datetime import datetime, time
from sqlalchemy.sql.expression import null


def insert_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='11',
        destination_area_code='11',
        start_at=time(hour=6),
        end_at=time(hour=21, minute=59, second=59))
    tariff_condition_2 = dbo.tariff_condition.insert(
        source_area_code='99',
        destination_area_code='41',
        start_at=time(hour=22),
        end_at=time(hour=5, minute=59, second=59))
    tariff_config_1 = dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime.now(),
        config_end_date=datetime.now(),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.09)
    tariff_config_2 = dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime.now(),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.09)
    call_start = dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=42,
        call_id=42,
        type='start',
        source_area_code='11',
        source='989889898',
        destination_area_code='11',
        destination='27227272',
        timestamp=datetime.now(),
        applied_tariff_config=tariff_config_1['id'])
    call_end = dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=4242,
        call_id=42,
        type='end',
        timestamp=datetime.now())


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_tariff_conditions(dbo):
    tariff_conditions = dbo.tariff_condition.select()
    assert len(tariff_conditions) == 2
    tariff_condition =  tariff_conditions[0]
    assert 'id' in tariff_condition
    assert tariff_condition['id'] > 0
    assert 'source_area_code' in tariff_condition
    assert 'destination_area_code' in tariff_condition
    assert 'start_at' in tariff_condition
    assert 'end_at' in tariff_condition
    where = [
        dbo.tariff_condition.source_area_code == '99',
        dbo.tariff_condition.destination_area_code == '41'
    ]
    tariff_conditions = dbo.tariff_condition.select(where=where)
    assert tariff_conditions
    assert len(tariff_conditions) == 1


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_tariff_config(dbo):
    tariff_configs = dbo.tariff_config.select()
    assert len(tariff_configs) == 2
    tariff_config = tariff_configs[0]
    assert 'id' in tariff_config
    assert 'created_date' in tariff_config
    assert 'config_start_date' in tariff_config
    assert 'config_end_date' in tariff_config
    assert 'conditions_id' in tariff_config
    assert 'standard_charge' in tariff_config
    assert 'call_time_charge' in tariff_config
    tariff_configs = dbo.tariff_config.select(where=[dbo.tariff_config.config_end_date == null()])
    print(tariff_configs)
    assert len(tariff_configs) == 1


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_call_records(dbo):
    call_records = dbo.call_record.select()
    assert len(call_records) == 2
    call_record = call_records[0]
    assert 'id' in call_record
    assert 'created_date' in call_record
    assert 'external_id' in call_record
    assert 'call_id' in call_record
    assert 'type' in call_record
    assert 'source_area_code' in call_record
    assert 'source' in call_record
    assert 'destination_area_code' in call_record
    assert 'destination' in call_record
    assert 'timestamp' in call_record
    assert 'applied_tariff_config' in call_record
    call_events = dbo.call_record.select(where=[dbo.call_record.call_id == 42])
    assert any([c for c in call_events if c['type'] == 'start'])
    assert any([c for c in call_events if c['type'] == 'end'])
