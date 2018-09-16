import pytest

from datetime import datetime, time
from unittest.mock import patch, MagicMock
from timebetween import is_time_between
from phone_bills.billingcommon.pricing import PriceEngine


CONFIG_ID_DT_RANGE_1 = 42
CONFIG_ID_DT_RANGE_2 = 4242
CONFIG_ID_DT_RANGE_3 = 424242


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
        id=CONFIG_ID_DT_RANGE_3,
        created_date=datetime.now(),
        config_start_date=datetime(2010, 1, 1),
        config_end_date=datetime(2050, 1, 1),
        conditions_id=tariff_condition_3['id'],
        standard_charge=0.36,
        call_time_charge=0.09)


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_get_config_one_period(dbo):
    engine = PriceEngine(dbo)
    start_at = datetime(2018, 1, 1, 21, 57, 13)
    end_at = datetime(2018, 1, 1, 21, 59, 59)
    configs = engine.get_tariff_configs(start_at, end_at, '41', '11')
    assert len(configs) == 1
    cfg = configs[0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_2


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_get_config_more_than_one_period(dbo):
    engine = PriceEngine(dbo)
    start_at = datetime(2018, 1, 1, 21, 57, 13)
    end_at = datetime(2018, 1, 1, 22, 17, 13)
    configs = engine.get_tariff_configs(start_at, end_at, '41', '11')
    assert len(configs) == 2
    cfg = [c for c in configs if c['order'] == 1][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_2
    cfg = [c for c in configs if c['order'] == 2][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_1

    start_at = datetime(2018, 1, 1, 21, 57, 13)
    end_at = datetime(2018, 1, 1, 5)
    configs = engine.get_tariff_configs(start_at, end_at, '41', '11')
    assert len(configs) == 3
    cfg = [c for c in configs if c['order'] == 1][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_2
    cfg = [c for c in configs if c['order'] == 2][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_1
    cfg = [c for c in configs if c['order'] == 3][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_3


# def insert_bill_call_data(dbo):
#     tariff_condition_1 = dbo.tariff_condition.insert(
#         source_area_code='99',
#         destination_area_code='99',
#         start_at=time(hour=22),
#         end_at=time(hour=21, minute=59, second=59))
#     tariff_config_1 = dbo.tariff_config.insert(
#         created_date=datetime.now(),
#         config_start_date=datetime(2015, 1, 1),
#         config_end_date=datetime(2015, 1, 31, 23, 59, 59),
#         conditions_id=tariff_condition_1['id'],
#         standard_charge=0.36,
#         call_time_charge=0.09)
#     dbo.call_record.insert(
#         created_date=datetime.now(),
#         external_id=123,
#         call_id=43,
#         type='start',
#         source_area_code='99',
#         source='988526423',
#         destination_area_code='99',
#         destination='93468278',
#         timestamp=datetime(2014, 12, 31, 23, 57, 13),
#         applied_tariff_config=tariff_config_1['id'])
#     dbo.call_record.insert(
#         created_date=datetime.now(),
#         external_id=124,
#         call_id=43,
#         type='end',
#         timestamp=datetime(2015, 1, 1, 0))
#     dbo.call_record.insert(
#         created_date=datetime.now(),
#         external_id=321,
#         call_id=44,
#         type='start',
#         source_area_code='99',
#         source='988526423',
#         destination_area_code='99',
#         destination='93468278',
#         timestamp=datetime(2015, 1, 31, 22),
#         applied_tariff_config=tariff_config_1['id'])
#     dbo.call_record.insert(
#         created_date=datetime.now(),
#         external_id=421,
#         call_id=44,
#         type='end',
#         timestamp=datetime(2015, 2, 1))


# @pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
# def test_get_bill_calls(dbo):
#     insert_bill_call_data(dbo)
#     price_engine = PriceEngine(dbo)
#     bill_calls = list(price_engine.get_bill_calls('99', '988526423', 1, 2015))
#     assert len(bill_calls) == 1
#     bill_call = bill_calls[0]
#     dt = datetime(2014, 12, 31, 23, 57, 13)
#     assert bill_call['destination'] == '9993468278'
#     assert bill_call['start_at'] == dt
#     assert bill_call['duration'] == time(0, 2, 47)
