import re

from datetime import datetime
from phone_bills.billingcommon.util import extract_phone_number


class CallRecordParser:
    def parse(self, call_record):
        call_event = dict(
            call_id=call_record['call_id'],
            external_id=call_record['id'],
            type=call_record['type'],
            timestamp=call_record['timestamp'])
        if 'source' in call_record:
            s_area_code, s_phone = extract_phone_number(call_record['source'])
            call_event['source_area_code'] = s_area_code
            call_event['source'] = s_phone
        if 'destination' in call_record:
            d_area_code, d_phone = extract_phone_number(call_record['destination'])
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
