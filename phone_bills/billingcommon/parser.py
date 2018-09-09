import re

from datetime import datetime

PHONE_NUMBER_RE = re.compile('^(?P<area_code>[0-9]{2})(?P<phone_number>[0-9]{8,9})$')


class CallRecordParser:
    def get_phone_number(self, phone_number):
        m = PHONE_NUMBER_RE.match(phone_number)
        if m:
            return m.group('area_code'), m.group('phone_number')
        raise ValueError('Not a phone number.')

    def parse(self, call_record):
        call_event = dict(
            call_id=call_record['call_id'],
            external_id=call_record['id'],
            type=call_record['type'],
            timestamp=call_record['timestamp'])
        if 'source' in call_record:
            s_area_code, s_phone = self.get_phone_number(call_record['source'])
            call_event['source_area_code'] = s_area_code
            call_event['source'] = s_phone
        if 'destination' in call_record:
            d_area_code, d_phone = self.get_phone_number(call_record['destination'])
            call_event['destination_area_code'] = d_area_code
            call_event['destination'] = d_phone
        ts = call_record['timestamp']
        if isinstance(ts, str):
            try:
                call_event['timestamp'] = datetime.strptime(
                    ts, '%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                call_event['timestamp'] = datetime.strptime(
                    ts, '%Y-%m-%dT%H:%M:%S.%fZ')

        return call_event
