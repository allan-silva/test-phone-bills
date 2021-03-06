import os

from pymongo import MongoClient, ASCENDING, DESCENDING


MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')


class BillingDocDb:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['heroku_9tl1g6wh']
        self.collection = self.db['bills']
        self.collection.create_index([('_id.subscriber', ASCENDING)])

    def insert_bill(self, subscriber, ref_month, ref_year, bill_calls, transaction_id):
        bill = self.create_bill_entry(subscriber, ref_month, ref_year, bill_calls, transaction_id)
        self.collection.save(bill)

    def get_bill(self, subscriber, ref_month, ref_year):
        if ref_month and ref_year:
            id = dict(subscriber=subscriber, month=ref_month, year=ref_year)
            return self.collection.find_one({'_id': id})
        sort_fields = [('_id.year', DESCENDING), ('_id.month', DESCENDING)]
        for d in self.collection.find({'_id.subscriber': subscriber})\
                                .sort(sort_fields)\
                                .limit(1):
            return d

    def create_bill_entry(self, subscriber, ref_month, ref_year, bill_calls, transaction_id):
        id = dict(subscriber=subscriber, month=ref_month, year=ref_year)
        return dict(_id=id, calls=bill_calls, transaction_id=transaction_id)


def configure_docdb(app):
    if not hasattr(app, 'docdb'):
        app.docdb = BillingDocDb()
