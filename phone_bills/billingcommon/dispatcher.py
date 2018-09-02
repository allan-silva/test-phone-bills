import os

from phone_bills.billingcommon.db import create_db
from phone_bills.billingcommon.service import PhoneCallService


billing_database = create_db(os.getenv('DATABASE_URL', 'postgresql://billingdb_user:billingdb_pwd@0.0.0.0:5432/billingdb'))


class MessageDispatcher:
    def __init__(self):
        self.__phone_call = PhoneCallService(billing_database)

    def phone_call(self, payload, message):
        transaction_id = message.headers.get('transaction_id')
        self.__phone_call.save(transaction_id, payload)


message_dispatcher = MessageDispatcher()
