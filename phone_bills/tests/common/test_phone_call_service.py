import pytest

from datetime import datetime, time
from phone_bills.billingcommon.service import PhoneCallService


CONFIG_ID_DT_RANGE_1 = 42
CONFIG_ID_DT_RANGE_2 = 4242


@pytest.fixture
def call_start_record():
    return {
        'id': 42,
        'type': 'start',
        'timestamp': '2017-12-12T21:57:13Z',
        'call_id': 71,
        'source': '41988526423',
        'destination': '1193468278'
    }


@pytest.fixture
def call_end_record():
    return {
        'id': 4242,
        'type': 'end',
        'timestamp': '2017-12-12T22:17:53Z',
        'call_id': 71
    }


def insert_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='41',
        destination_area_code='11',
        start_at=time(hour=22),
        end_at=time(hour=4, minute=59, second=59))
    tariff_condition_2 = dbo.tariff_condition.insert(
        source_area_code='41',
        destination_area_code='11',
        start_at=time(hour=6),
        end_at=time(hour=21, minute=59, second=59))
    tariff_condition_3 = dbo.tariff_condition.insert(
        source_area_code='41',
        destination_area_code='11',
        start_at=time(hour=5),
        end_at=time(hour=5, minute=59, second=59))
    dbo.tariff_config.insert(
        id=CONFIG_ID_DT_RANGE_1,
        created_date=datetime.now(),
        config_start_date=datetime(2010, 1, 1),
        config_end_date=datetime(2050, 1, 1),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0)
    dbo.tariff_config.insert(
        id=CONFIG_ID_DT_RANGE_2,
        created_date=datetime.now(),
        config_start_date=datetime(2010, 1, 1),
        config_end_date=datetime(2050, 1, 1),
        conditions_id=tariff_condition_2['id'],
        standard_charge=0.36,
        call_time_charge=0.09)
    dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime(2010, 1, 1),
        config_end_date=datetime(2050, 1, 1),
        conditions_id=tariff_condition_3['id'],
        standard_charge=0.36,
        call_time_charge=0.09)


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_save_calls(dbo, call_start_record, call_end_record):
    service = PhoneCallService(dbo)
    service.save('tid', call_start_record)
    service.save('tid2', call_end_record)
    where = [
        dbo.call_record.external_id == 42,
        dbo.call_record.call_id == 71,
        dbo.call_record.type == 'start',
        dbo.call_record.source_area_code == '41',
        dbo.call_record.source == '988526423',
        dbo.call_record.destination_area_code == '11',
        dbo.call_record.destination == '93468278',
        dbo.call_record.timestamp == datetime(2017, 12, 12, 21, 57, 13)
    ]
    calls = dbo.call_record.select(where)
    assert len(calls) == 1

    call_start = calls[0]

    where = [
        dbo.call_record.external_id == 4242,
        dbo.call_record.call_id == 71,
        dbo.call_record.type == 'end',
        dbo.call_record.timestamp == datetime(2017, 12, 12, 22, 17, 53)
    ]
    calls = dbo.call_record.select(where)
    assert len(calls) == 1

    where = [dbo.applied_config.call_id == call_start['id']]
    applied_configs = dbo.applied_config.select(where=where)
    assert len(applied_configs) == 2

    applied_cfg = [c for c in applied_configs if c['config_id'] == CONFIG_ID_DT_RANGE_1][0]
    assert applied_cfg['order'] == 2
    assert applied_cfg['start_at'] == datetime(2017, 12, 12, 22)
    assert applied_cfg['end_at'] == datetime(2017, 12, 12, 22, 17, 53)
    assert applied_cfg['standard_charge'] == 0.36
    assert applied_cfg['call_time_charge'] == 0

    applied_cfg = [c for c in applied_configs if c['config_id'] == CONFIG_ID_DT_RANGE_2][0]
    assert applied_cfg['order'] == 1
    assert applied_cfg['start_at'] == datetime(2017, 12, 12, 21, 57, 13)
    assert applied_cfg['end_at'] == datetime(2017, 12, 12, 21, 59, 59)
    assert applied_cfg['standard_charge'] == 0.36
    assert applied_cfg['call_time_charge'] == 0.09


def test_save_error(dbo, call_start_record):
    service = PhoneCallService(dbo)
    call_start_record['source'] = '99234'
    with pytest.raises(ValueError):
        service.save('tid3', call_start_record)
