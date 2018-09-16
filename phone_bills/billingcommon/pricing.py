from calendar import monthrange
from datetime import datetime, time

# This is a external package, but I'm the author
# https://github.com/MicroarrayTecnologia/py-time-between
from timebetween import is_time_between
from phone_bills.billingcommon.util import call_duration, time_add


class PriceEngine:
    def __init__(self, db):
        self.db = db

    def is_config_applicable(self, time, config):
        return is_time_between(time, config['start_at'], config['end_at'])

    def get_tariff_configs(self, start_at, end_at, source_area_code, dest_area_code):
        applied_configs = []
        start_time = start_at.time()
        end_time = end_at.time()
        configs = self.db.tariff_config.get_current_configs(
            source_area_code, dest_area_code, start_at)

        def get_config(t):
            for c in configs:
                if self.is_config_applicable(t, c):
                    return c
            return None

        config_order = 0
        config = get_config(start_time)

        while config:
            config_order += 1
            applied_config = dict(
                config_id=config['config_id'],
                start_time=start_time,
                standard_charge=config['standard_charge'],
                call_time_charge=config['call_time_charge'],
                order=config_order)
            if self.is_config_applicable(end_time, config):
                applied_config['end_time'] = end_time
                applied_configs.append(applied_config)
                break
            else:
                applied_config['end_time'] = config['end_at']
                start_time = time_add(config['end_at'], s=1)
                applied_configs.append(applied_config)
            config = get_config(start_time)

        return applied_configs


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
                       start_at=bill_call['start_at'],
                       duration=self.get_call_time(bill_call),
                       price=self.get_call_charge(bill_call))
