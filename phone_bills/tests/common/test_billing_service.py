import pytest

from unittest.mock import patch, MagicMock
from datetime import datetime, time
from phone_bills.billingcommon.service import BillingService


def insert_data(dbo):
    tariff_condition_1 = dbo.tariff_condition.insert(
        source_area_code='41',
        destination_area_code='11',
        start_at=time(hour=22),
        end_at=time(hour=4, minute=59, second=59))
    config_1 = dbo.tariff_config.insert(
        created_date=datetime.now(),
        config_start_date=datetime(2010, 1, 1),
        config_end_date=datetime(2050, 1, 1),
        conditions_id=tariff_condition_1['id'],
        standard_charge=0.36,
        call_time_charge=0.42)
    call_start_1 = dbo.call_record.insert(dict(
        created_date = datetime.now(),
        external_id = 4001,
        call_id = 40,
        type = 'start',
        source_area_code = '41',
        source = '11111111',
        destination_area_code = '11',
        destination = '222222222',
        timestamp = datetime(2010, 12, 31, 23, 57, 13),
        transaction_id = '1'))
    call_end_1 = dbo.call_record.insert(dict(
        created_date = datetime.now(),
        external_id = 4002,
        call_id = 40,
        type = 'end',
        timestamp = datetime(2011, 1, 1, 0, 17, 53),
        transaction_id = '1'))
    dbo.applied_config.insert(
        call_id = call_start_1['id'],
        config_id = config_1['id'],
        start_at = datetime(2010, 12, 31, 23, 57, 13),
        end_at = datetime(2011, 1, 1, 0, 17, 53),
        standard_charge = 0.36,
        call_time_charge = 0.42,
        order = 1)


@pytest.mark.parametrize('dbo', [insert_data], indirect=['dbo'])
def test_close_bill(dbo):
    with patch('phone_bills.billingcommon.docdb.BillingDocDb') as DocDb:
        mock_instance = DocDb()
        service = BillingService(dbo, mock_instance)
        close_request = dict(subscriber='4111111111', ref=dict(month=1, year=2011))
        service.close_bill('1', close_request)
        assert mock_instance.insert_bill.call_count == 1
        calls= [
            dict(
                call_id='40',
                destination='11222222222',
                start_at=datetime(2010, 12, 31, 23, 57, 13),
                duration=dict(d=0, h=0, m=20, s=40),
                price=(0.36+(0.42*20)))
        ]
        mock_instance.insert_bill.assert_called_with(
            '4111111111', 1, 2011, calls, '1')
