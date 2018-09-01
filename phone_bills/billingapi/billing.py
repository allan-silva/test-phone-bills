from flask import current_app as app


def get_info():
    for i in range(0, 10):
        app.amqp.info.publish({'id': i, 'info_requested': True})
    return {'status': 'OK'}


def call_event():
    pass
