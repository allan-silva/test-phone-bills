from calendar import monthrange
from datetime import datetime, time, timedelta

# This is an external package, but I'm the author
# https://github.com/MicroarrayTecnologia/py-time-between
from timebetween import is_time_between
from phone_bills.billingcommon.logging import configure_log
from phone_bills.billingcommon.util import call_duration, time_add, walk_in_time


class PriceEngine:
    def __init__(self, db):
        self.db = db
        configure_log(self, PriceEngine.__name__)

    def is_config_applicable(self, time, config):
        return is_time_between(time, config['start_at'], config['end_at'])

    def get_tariff_configs(self, start_at, end_at, source_area_code, dest_area_code):
        applied_configs = []

        configs = self.db.tariff_config.get_current_configs(
            source_area_code, dest_area_code, start_at)

        def get_config(t):
            for c in configs:
                if self.is_config_applicable(t, c):
                    return c
            return None

        config_order = 0
        start_date = start_at
        while start_date <= end_at:
            start_time = start_date.time()
            config = get_config(start_time)
            if not configs:
                break
            end_date = walk_in_time(start_date, end_at, config['end_at'])
            end_time = end_date.time()
            config_order += 1
            applied_config = dict(
                config_id=config['config_id'],
                start_at=start_date,
                end_at=end_date,
                standard_charge=config['standard_charge'],
                call_time_charge=config['call_time_charge'],
                order=config_order)
            applied_configs.append(applied_config)
            start_date = end_date + timedelta(seconds=1)
        return applied_configs

    def get_call_charge(self, bill_call):
        charges = []
        orders = [config['order'] for config in bill_call['configs']]
        min_order, max_order = min(orders), max(orders)
        for config in bill_call['configs']:
            charge = 0
            if config['order'] == min_order:
                charge += config['standard_charge']
            minutes = call_duration(config['start_at'], config['end_at'])
            charge += minutes * config['call_time_charge']
            transition_time_conditions = [
                config['order'] > min_order,
                config['order'] < max_order
            ]
            if all(transition_time_conditions):
                charge += config['call_time_charge']
            charges.append(charge)
        return sum(charges)

    def get_bill_calls(self, area_code, phone_number, ref_month, ref_year):
        start_date = datetime(ref_year, ref_month, 1)
        _, last_day = monthrange(ref_year, ref_month)
        end_date = datetime(ref_year, ref_month, last_day, 23, 59, 59)
        for bill_call in self.db.call_record.calls_for_pricing(
            area_code, phone_number, start_date, end_date):
            yield dict(call_id=bill_call['call_id'],
                       destination=f"{bill_call['area_code']}{bill_call['phone']}",
                       start_at=bill_call['start_at'],
                       duration=bill_call['end_at'] - bill_call['start_at'],
                       price=self.get_call_charge(bill_call))
