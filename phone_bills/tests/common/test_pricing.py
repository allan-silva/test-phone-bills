import pytest

from datetime import datetime, time, date
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
    assert cfg['start_at'] == start_at
    assert cfg['end_at'] == end_at
    assert cfg['standard_charge'] == 0.36
    assert cfg['call_time_charge'] == 0.09
    assert cfg['order'] == 1


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_get_config_more_than_one_period(dbo):
    engine = PriceEngine(dbo)
    start_at = datetime(2018, 1, 1, 21, 57, 13)
    end_at = datetime(2018, 1, 1, 22, 17, 13)
    configs = engine.get_tariff_configs(start_at, end_at, '41', '11')
    assert len(configs) == 2
    cfg = [c for c in configs if c['order'] == 1][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_2
    assert cfg['start_at'] == datetime(2018, 1, 1, 21, 57, 13)
    assert cfg['end_at'] == datetime(2018, 1, 1, 21, 59, 59)
    assert cfg['standard_charge'] == 0.36
    assert cfg['call_time_charge'] == 0.09

    cfg = [c for c in configs if c['order'] == 2][0]
    assert cfg['config_id'] == CONFIG_ID_DT_RANGE_1
    assert cfg['start_at'] == datetime(2018, 1, 1, 22)
    assert cfg['end_at'] == datetime(2018, 1, 1, 22, 17, 13)
    assert cfg['standard_charge'] == 0.36
    assert cfg['call_time_charge'] == 0.0


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_long_time_pariod(dbo):
    engine = PriceEngine(dbo)
    start_at = datetime(2016, 2, 28, 5, 30, 49)
    end_at = datetime(2016, 3, 1, 22, 17, 13)
    configs = engine.get_tariff_configs(start_at, end_at, '41', '11')
    assert len(configs) == 9
    day28 = date(2016, 2, 28)
    day29 = date(2016, 2, 29)
    day1 = date(2016, 3, 1)
    time1 = time(5)
    time2 = time(5, 59, 59)
    time3 = time(6)
    time4 = time(21, 59, 59)
    time5 = time(22)
    time6 = time(4, 59, 59)

    # 1 28 05:30:49 - 28 05:59:59
    cfg = [c for c in configs if c['order'] == 1][0]
    assert cfg['start_at'] == datetime.combine(day28, time(5, 30, 49))
    assert cfg['end_at'] == datetime.combine(day28, time2)

    # 2 28 06:00:00 - 28 21:59:59
    cfg = [c for c in configs if c['order'] == 2][0]
    assert cfg['start_at'] == datetime.combine(day28, time3)
    assert cfg['end_at'] == datetime.combine(day28, time4)

    # 3 28 22:00:00 - 29 04:59:59
    cfg = [c for c in configs if c['order'] == 3][0]
    assert cfg['start_at'] == datetime.combine(day28, time5)
    assert cfg['end_at'] == datetime.combine(day29, time6)

    # 4 29 05:00:00 - 29 05:59:59
    cfg = [c for c in configs if c['order'] == 4][0]
    assert cfg['start_at'] == datetime.combine(day29, time1)
    assert cfg['end_at'] == datetime.combine(day29, time2)

    # 5 29 06:00:00 - 29 21:59:59
    cfg = [c for c in configs if c['order'] == 5][0]
    assert cfg['start_at'] == datetime.combine(day29, time3)
    assert cfg['end_at'] == datetime.combine(day29, time4)

    # 6 29 22:00:00 - 01 04:59:59
    cfg = [c for c in configs if c['order'] == 6][0]
    assert cfg['start_at'] == datetime.combine(day29, time5)
    assert cfg['end_at'] == datetime.combine(day1, time6)

    # 7 01 05:00:00 - 01 05:59:59
    cfg = [c for c in configs if c['order'] == 7][0]
    assert cfg['start_at'] == datetime.combine(day1, time1)
    assert cfg['end_at'] == datetime.combine(day1, time2)

    # 8 01 06:00:00 - 01 21:59:59
    cfg = [c for c in configs if c['order'] == 8][0]
    assert cfg['start_at'] == datetime.combine(day1, time3)
    assert cfg['end_at'] == datetime.combine(day1, time4)

    # 9 01 22:00:00 - 01 22:17:13
    cfg = [c for c in configs if c['order'] == 9][0]
    assert cfg['start_at'] == datetime.combine(day1, time5)
    assert cfg['end_at'] == datetime.combine(day1, time(22, 17, 13))


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
