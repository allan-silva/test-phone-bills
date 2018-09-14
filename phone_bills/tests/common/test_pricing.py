import pytest

from datetime import datetime, time
from unittest.mock import patch, MagicMock
from timebetween import is_time_between
from phone_bills.billingcommon.pricing import PriceEngine


CONFIG_ID_DT_RANGE_1 = 42
CONFIG_ID_DT_RANGE_2 = 4242


@pytest.fixture()
def call_record():
    return dict(type='start',
                source_area_code='41',
                destination_area_code='11')


def insert_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='41',
        destination_area_code='11',
        start_at=time(hour=22),
        end_at=time(hour=5, minute=59, second=59))
    dbo.tariff_config.insert(
        id=CONFIG_ID_DT_RANGE_1,
        created_date=datetime.now(),
        config_start_date=datetime(2018, 8, 7, 22),
        config_end_date=datetime(2018, 8, 15, 18, 25, 30),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.09)
    dbo.tariff_config.insert(
        id=CONFIG_ID_DT_RANGE_2,
        created_date=datetime.now(),
        config_start_date=datetime(2018, 8, 15, 18, 25, 31),
        config_end_date=datetime(2018, 8, 30),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.1,
        call_time_charge=0.15)


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_get_config(dbo, call_record):
    price_engine = PriceEngine(dbo)
    call_record['timestamp'] = datetime(2018, 8, 7, 22)
    config = price_engine.get_tariff_config(call_record)
    assert config['config_id'] == CONFIG_ID_DT_RANGE_1

    call_record['timestamp'] = datetime(2018, 8, 13, 3)
    config = price_engine.get_tariff_config(call_record)
    assert config['config_id'] == CONFIG_ID_DT_RANGE_1

    call_record['timestamp'] = datetime(2018, 8, 15, 5, 59, 59)
    config = price_engine.get_tariff_config(call_record)
    assert config['config_id'] == CONFIG_ID_DT_RANGE_1

    call_record['timestamp'] = datetime(2018, 8, 15, 22)
    config = price_engine.get_tariff_config(call_record)
    assert config['config_id'] == CONFIG_ID_DT_RANGE_2


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_no_config_error_not_fall_in_range(dbo, call_record):
    price_engine = PriceEngine(dbo)
    call_record['timestamp'] = datetime(2018, 8, 15, 21, 59, 59)
    with patch.object(PriceEngine,
                      'is_config_applicable',
                      wraps=lambda t, c: is_time_between(t, c['start_at'], c['end_at'])) as mock:
        with pytest.raises(RuntimeError):
            price_engine.get_tariff_config(call_record)
        assert mock.call_count == 1


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_no_config_error_no_config_exists(dbo, call_record):
    price_engine = PriceEngine(dbo)
    call_record['timestamp'] = datetime(2018, 8, 30, 0, 0, 1)
    with patch.object(PriceEngine,
                      'is_config_applicable',
                      wraps=lambda t, c: is_time_between(t, c['start_at'], c['end_at'])) as mock:
        with pytest.raises(RuntimeError):
            price_engine.get_tariff_config(call_record)
        assert mock.call_count == 0


def test_apply_tariff_config_error():
    price_engine = PriceEngine(None)
    with pytest.raises(ValueError):
        price_engine.get_tariff_config({'type': 'end'})


def insert_bill_call_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='99',
        destination_area_code='99',
        start_at=time(hour=22),
        end_at=time(hour=21, minute=59, second=59))
    tariff_config_1 = dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime(2015, 1, 1),
        config_end_date=datetime(2015, 1, 31, 23, 59, 59),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.09)
    dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=123,
        call_id=43,
        type='start',
        source_area_code='99',
        source='988526423',
        destination_area_code='99',
        destination='93468278',
        timestamp=datetime(2014, 12, 31, 23, 57, 13),
        applied_tariff_config=tariff_config_1['id'])
    dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=124,
        call_id=43,
        type='end',
        timestamp=datetime(2015, 1, 1, 0))
    dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=321,
        call_id=44,
        type='start',
        source_area_code='99',
        source='988526423',
        destination_area_code='99',
        destination='93468278',
        timestamp=datetime(2015, 1, 31, 22),
        applied_tariff_config=tariff_config_1['id'])
    dbo.call_record.insert(
        created_date=datetime.now(),
        external_id=421,
        call_id=44,
        type='end',
        timestamp=datetime(2015, 2, 1))


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_get_bill_calls(dbo):
    insert_bill_call_data(dbo)
    price_engine = PriceEngine(dbo)
    bill_calls = list(price_engine.get_bill_calls('99', '988526423', 1, 2015))
    assert len(bill_calls) == 1
    bill_call = bill_calls[0]
    dt = datetime(2014, 12, 31, 23, 57, 13)
    assert bill_call['destination'] == '9993468278'
    assert bill_call['call_start_at'] == dt
    assert bill_call['call_duration'] == time(0, 2, 47)
