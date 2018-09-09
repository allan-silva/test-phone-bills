# This is a external package, but I'm the author
# https://github.com/MicroarrayTecnologia/py-time-between
from timebetween import is_time_between


class PriceEngine:
    def __init__(self, db):
        self.db = db

    def is_config_applicable(self, time, config):
        print(time, config['start_at'], config['end_at'])
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
