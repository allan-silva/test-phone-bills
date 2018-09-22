import uuid

from connexion import request


def register_transaction_request_generator(app):
    @app.before_request
    def create_transaction_id():
        request.transaction_id = uuid.uuid4()


def get_transaction():
    return {'transaction_id': str(request.transaction_id)}


def with_transaction(f):
    def decorated(*args, **kwargs):
        return f(*args, transaction=get_transaction(), **kwargs)
    return decorated
