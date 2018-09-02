from connexion import request, problem
from flask import current_app as app

from phone_bills.billingapi.transaction import with_transaction
from phone_bills.billingapi.validation import validate_call_record


@with_transaction
def get_info(transaction):
    app.log.info("Info requested")
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
