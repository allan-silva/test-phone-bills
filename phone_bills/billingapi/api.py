import connexion
import phone_bills.billingapi.json_schema_format # Bringing the formatters checkers to context

from phone_bills.billingapi.transaction import register_transaction_request_generator
from phone_bills.billingmq.producer import configure_producer


def create_app_with_swagger():
    connexion_app = connexion.App(__name__,
                                  specification_dir='swagger/',
                                  validate_responses=True)
    connexion_app.add_api('api.yaml')
    return connexion_app.app


def create_app():
    app = create_app_with_swagger()
    register_transaction_request_generator(app)
    configure_producer(app, 'info', 'phone-calls.dx', 'get-info')
    configure_producer(app, 'call_event', 'phone-calls.dx', 'call-event')
    return app
