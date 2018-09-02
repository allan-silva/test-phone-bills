from phone_bills.billingcommon.logging import configure_log


class PhoneCallService:
    def __init__(self, db):
        self.db = db
        configure_log(self, __name__)

    def save(self, transaction_id, call_record):
        self.log.info(f'Call Record received\nTransaction: {transaction_id}\nRecord: {call_record}')
