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

    def save(self, transaction_id, call_record):
        self.log.info(f'Call Record received - {transaction_id} - Record: {call_record}')
        try:
            call_record = self.parser.parse(call_record)
            call_record['transaction_id'] = transaction_id
            if call_record['type'] == 'start':
                config = self.price_engine.get_tariff_config(call_record)
                call_record['applied_tariff_config'] = config['config_id']
            self.db.call_record.insert(**call_record)
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
        return dict(h=duration.hour, m=duration.minute, s=duration.second)

    def close_bill(self, transaction_id, close_request):
        self.log.info(f'Bill close requested: {transaction_id} - {close_request}')
        area_code, phone = extract_phone_number(close_request['subscriber'])
        month, year = int(close_request['ref']['month']), int(close_request['ref']['year'])
        calls = []
        for bill_call in self.price_engine.get_bill_calls(area_code, phone, month, year):
            bill_call['duration'] = self.create_call_duration(bill_call)
            calls.append(bill_call)
        bill_entry = self.doc_db.create_bill_entry(
            close_request['subscriber'],
            month,
            year,
            calls,
            transaction_id)
        self.doc_db.insert_bill(bill_entry)
