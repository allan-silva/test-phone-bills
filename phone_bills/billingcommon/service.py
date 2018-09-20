from phone_bills.billingcommon.parser import CallRecordParser
from phone_bills.billingcommon.pricing import PriceEngine
from phone_bills.billingcommon.logging import configure_log
from phone_bills.billingcommon.util import extract_phone_number


class PhoneCallService:
    def __init__(self, db):
        self.db = db
        self.parser = CallRecordParser()
        self.price_engine = PriceEngine(self.db)
        configure_log(self, PhoneCallService.__name__)

    def get_related_call_record(self, call_record):
        where = [
            self.db.call_record.call_id == call_record['call_id'],
            self.db.call_record.type != call_record['type']
        ]
        records = self.db.call_record.select(where=where)
        return records[0] if records else None

    def get_configs(self, call_start_record, call_end_record):
        configs = self.price_engine.get_tariff_configs(
            call_start_record['timestamp'],
            call_end_record['timestamp'],
            call_start_record['source_area_code'],
            call_start_record['destination_area_code'])
        return configs

    def save_config(self, call_record):
        related_call_record = self.get_related_call_record(call_record)
        if related_call_record:
            if call_record['type'] == 'start':
                call_start_record = call_record
                call_end_record = related_call_record
            else:
                call_start_record = related_call_record
                call_end_record = call_record
            configs = self.get_configs(call_start_record, call_end_record)
            for config in configs:
                config['call_id'] = call_start_record['id']
                self.db.applied_config.insert(**config)

    def call_record_exists(self, call_record):
        where = [
            self.db.call_record.call_id == call_record['call_id'],
            self.db.call_record.type == call_record['type']
        ]

        if call_record['type'] == 'start':
            where_start = [
                self.db.call_record.source_area_code == call_record['source_area_code'],
                self.db.call_record.source == call_record['source'],
                self.db.call_record.destination_area_code == call_record['destination_area_code'],
                self.db.call_record.destination == call_record['destination']
            ]
            where.extend(where_start)

        call_records = self.db.call_record.select(where=where)
        return bool(call_records)

    def save(self, transaction_id, call_record):
        self.log.info(f'Call Record received - {transaction_id} - Record: {call_record}')
        try:
            call_record = self.parser.parse(call_record)
            if self.call_record_exists(call_record):
                self.log.warn(f'{transaction_id} - Call record already exists, ignoring...')
                return
            call_record['transaction_id'] = transaction_id
            ret = self.db.call_record.insert(call_record)
            call_record['id'] = ret['id']
            self.save_config(call_record)
        except Exception:
            self.log.exception('Error inserting call record')
            raise


class BillingService:
    def __init__(self, db, doc_db):
        self.db = db
        self.doc_db = doc_db
        self.price_engine = PriceEngine(self.db)
        configure_log(self, BillingService.__name__)

    def create_call_duration(self, bill_call):
        duration = bill_call['duration']
        hours, remain_secs = divmod(duration.seconds, 3600)
        minutes, secs = divmod(remain_secs, 60)
        return dict(d=duration.days, h=hours, m=minutes, s=secs)

    def close_bill(self, transaction_id, close_request):
        self.log.info(f'Bill close requested: {transaction_id} - {close_request}')
        area_code, phone = extract_phone_number(close_request['subscriber'])
        month, year = int(close_request['ref']['month']), int(close_request['ref']['year'])
        calls = []
        for bill_call in self.price_engine.get_bill_calls(area_code, phone, month, year):
            bill_call['duration'] = self.create_call_duration(bill_call)
            calls.append(bill_call)
        self.doc_db.insert_bill(
            close_request['subscriber'],
            month,
            year,
            calls,
            transaction_id)
