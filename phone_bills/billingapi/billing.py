from connexion import request, problem
from flask import current_app as app

from phone_bills.billingapi.transaction import with_transaction
from phone_bills.billingapi.parser import BillResponseParser
from phone_bills.billingapi.validation import validate_call_record


bill_parser = BillResponseParser()


@with_transaction
def get_info(transaction):
    app.log.info("Info requested")
    app.amqp.info.publish(transaction, headers=transaction)
    return transaction


@with_transaction
def call_event(call_record, transaction):
    validation_result = validate_call_record(call_record)
    if not validation_result.is_valid:
        return problem(400,
                       'Invalid CallRecord',
                       validation_result.message,
                       ext=transaction)
    app.amqp.call_event.publish(call_record, headers=transaction)
    return transaction, 202


@with_transaction
def bill_close(subscriber, ref_period, transaction):
    close_request = dict(subscriber=subscriber, ref=ref_period)
    app.amqp.bill_event.publish(close_request, headers=transaction)
    return transaction, 202


def get_bill(subscriber, month=None, year=None):
    try:
        bill = app.docdb.get_bill(subscriber, month, year)
        if bill:
            return bill_parser.parse(bill), 200
        return problem(404, 'Not found', 'Phone Bill not found.')
    except Exception:
        app.log.exception('Error requesting phone bill.')
        raise
