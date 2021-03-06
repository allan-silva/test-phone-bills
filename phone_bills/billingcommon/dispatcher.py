import os

from phone_bills.billingcommon.db import create_db
from phone_bills.billingcommon.docdb import BillingDocDb
from phone_bills.billingcommon.service import PhoneCallService, BillingService


db_url = os.getenv('DATABASE_URL', 'postgresql://billingdb_user:billingdb_pwd@0.0.0.0:5432/billingdb')
billing_database = create_db(db_url)
billing_doc_db = BillingDocDb()


class MessageDispatcher:
    def __init__(self):
        self.__call_service = PhoneCallService(billing_database)
        self.__billing_service = BillingService(billing_database, billing_doc_db)

    def phone_call(self, payload, message):
        transaction_id = message.headers.get('transaction_id')
        self.__call_service.save(transaction_id, payload)

    def bill_close(self, payload, message):
        transaction_id = message.headers.get('transaction_id')
        self.__billing_service.close_bill(transaction_id, payload)


message_dispatcher = MessageDispatcher()
