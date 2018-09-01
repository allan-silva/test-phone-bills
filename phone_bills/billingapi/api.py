import connexion
from phone_bills.billingmq.producer import configure_producer


def create_app_with_swagger():
    connexion_app = connexion.App(__name__, specification_dir='swagger/')
    connexion_app.add_api('api.yaml')
    return connexion_app.app


def create_app():
    app = create_app_with_swagger()
    configure_producer(app, 'info', 'phone-calls.dx', 'get-info')
    return app
