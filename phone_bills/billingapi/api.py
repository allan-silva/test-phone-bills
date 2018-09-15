import connexion
import phone_bills.billingapi.json_schema_format # Bringing the formatters checkers to context

from phone_bills.billingapi.transaction import register_transaction_request_generator
from phone_bills.billingcommon.docdb import configure_docdb
from phone_bills.billingcommon.logging import configure_log
from phone_bills.billingmq.producer import configure_producer


def create_app_with_swagger():
    connexion_app = connexion.App(__name__,
                                  specification_dir='swagger/',
                                  validate_responses=True)
    connexion_app.add_api('api.yaml')
    return connexion_app.app


def create_app():
    app = create_app_with_swagger()
    configure_log(app, __name__)
    configure_docdb(app)
    register_transaction_request_generator(app)
    configure_producer(app, 'info', 'call-event.tx', 'get-info')
    configure_producer(app, 'call_event', 'call-event.tx', 'call-event')
    configure_producer(app, 'bill_event', 'bill-event.tx', 'bill-close')
    return app
