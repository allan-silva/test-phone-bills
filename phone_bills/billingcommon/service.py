from phone_bills.billingcommon.parser import CallRecordParser
from phone_bills.billingcommon.pricing import PriceEngine
from phone_bills.billingcommon.logging import configure_log


class PhoneCallService:
    def __init__(self, db):
        self.db = db
        self.parser = CallRecordParser()
        self.price_engine = PriceEngine(self.db)
        configure_log(self, __name__)

    def save(self, transaction_id, call_record):
        self.log.info(f'Call Record received\nTransaction: {transaction_id}\nRecord: {call_record}')
        try:
            call_record = self.parser.parse(call_record)
            if call_record['type'] == 'start':
                config = self.price_engine.get_tariff_config(call_record)
                call_record['applied_tariff_config'] = config['config_id']
            self.db.call_record.insert(**call_record)
        except Exception:
            self.log.exception('Error inserting call record')
            raise

