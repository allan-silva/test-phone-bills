from calendar import monthrange
from datetime import datetime, time

# This is a external package, but I'm the author
# https://github.com/MicroarrayTecnologia/py-time-between
from timebetween import is_time_between
from phone_bills.billingcommon.util import call_duration


class PriceEngine:
    def __init__(self, db):
        self.db = db

    def is_config_applicable(self, time, config):
        return is_time_between(time, config['start_at'], config['end_at'])

    def get_tariff_config(self, call_record):
        if call_record['type'] != 'start':
            raise ValueError('Call start record is expected.')
        timestamp = call_record['timestamp']
        configs = self.db.tariff_config.get_current_configs(
            call_record['source_area_code'],
            call_record['destination_area_code'],
            timestamp)
        for config in configs:
            if self.is_config_applicable(timestamp.time(), config):
                return config
        raise RuntimeError('No tariff config for call record.')

    def get_call_charge(self, bill_call):
        call_time = call_duration(bill_call['start_at'], bill_call['end_at'])
        time_charge = call_time * bill_call['call_time_charge']
        return bill_call['standard_charge'] + time_charge

    def get_call_time(self, bill_call):
        call_time = bill_call['end_at'] - bill_call['start_at']
        call_duration = datetime.combine(datetime.today(), time()) + call_time
        return call_duration.time()

    def get_bill_calls(self, area_code, phone_number, ref_month, ref_year):
        start_date = datetime(ref_year, ref_month, 1)
        _, last_day = monthrange(ref_year, ref_month)
        end_date = datetime(ref_year, ref_month, last_day, 23, 59, 59)
        for bill_call in self.db.call_record.calls_for_pricing(
            area_code, phone_number, start_date, end_date):
            yield dict(destination=f"{bill_call['area_code']}{bill_call['phone']}",
                       call_start_at=bill_call['start_at'],
                       call_duration=self.get_call_time(bill_call),
                       call_price=self.get_call_charge(bill_call))
