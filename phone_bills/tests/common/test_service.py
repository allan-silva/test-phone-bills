import pytest

from datetime import datetime, time
from phone_bills.billingcommon.service import PhoneCallService


@pytest.fixture
def call_start_record():
    return {
        'id': 42,
        'type': 'start',
        'timestamp': '2017-12-12T15:07:13Z',
        'call_id': 71,
        'source': '99988526423',
        'destination': '9993468278'
    }


@pytest.fixture
def call_end_record():
    return {
        'id': 442,
        'type': 'end',
        'timestamp': '2017-12-12T15:14:56Z',
        'call_id': 71
    }


def insert_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='99',
        destination_area_code='99',
        start_at=time(hour=6),
        end_at=time(hour=21, minute=59, second=59))
    dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime(2017,1, 1),
        config_end_date=datetime(2018, 1, 1),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.09)


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_save_call_start(dbo, call_start_record):
    service = PhoneCallService(dbo)
    service.save('tid', call_start_record)
    where = [
        dbo.call_record.external_id == 42,
        dbo.call_record.call_id == 71,
        dbo.call_record.type == 'start',
        dbo.call_record.source_area_code == '99',
        dbo.call_record.source == '988526423',
        dbo.call_record.destination_area_code == '99',
        dbo.call_record.destination == '93468278',
        dbo.call_record.timestamp == datetime(2017, 12, 12, 15, 7, 13)
    ]
    calls = dbo.call_record.select(where)
    assert len(calls) == 1


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_save_call_end(dbo, call_end_record):
    service = PhoneCallService(dbo)
    service.save('tid2', call_end_record)
    where = [
        dbo.call_record.external_id == 442,
        dbo.call_record.call_id == 71,
        dbo.call_record.type == 'end',
        dbo.call_record.timestamp == datetime(2017, 12, 12, 15, 14, 56)
    ]
    calls = dbo.call_record.select(where)
    assert len(calls) == 1


def test_save_error(dbo, call_start_record):
    service = PhoneCallService(dbo)
    call_start_record['source'] = '99234'
    with pytest.raises(ValueError):
        service.save('tid3', call_start_record)
