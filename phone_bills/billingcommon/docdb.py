import os

from datetime import datetime
from pymongo import MongoClient, ASCENDING


MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')


class BillingDocDb:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['heroku_9tl1g6wh']
        self.collection = self.db['bills']
        self.collection.create_index([('_id.subscriber', ASCENDING)])

    def insert_bill(self, bill):
        self.collection.save(bill)

    def get_bill(self, subscriber, ref_month, ref_year):
        id = dict(subscriber=subscriber, month=ref_month, year=ref_year)
        return self.collection.find_one({'_id': id})

    def create_bill_entry(self, subscriber, ref_month, ref_year, bill_calls, transaction_id):
        id = dict(subscriber=subscriber, month=ref_month, year=ref_year)
        return dict(_id=id, calls=bill_calls, transaction_id=transaction_id)


def configure_producer(app, name, exchange, routing_key, serializer='json'):
    if not hasattr(app, 'amqp'):
        app.amqp = AmqpExtension()
    app.amqp.add_producer(name, exchange, routing_key, serializer)


if __name__ == '__main__':
    from datetime import time
    doc_db = BillingDocDb()
    entry = doc_db.create_bill_entry('11989889898', 10, 2015, [time(11,0)], 'we')
    doc_db.insert_bill(entry)
    print(doc_db.get_bill('11989889898', 10, 2015))
