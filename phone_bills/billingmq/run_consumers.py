from phone_bills.billingcommon.logging import configure_log
from phone_bills.billingmq.consumer import QueueHandler, BillingConsumers


class Logger:
    pass

logger = Logger()
configure_log(logger, __name__)


def on_message(body, message):
    logger.log.info(f'Consumers setup test: \nMessage: {message}\nHeaders: {message.headers}\nBody: {body}')


def run():
    queue_handlers = [
        QueueHandler('call-event', on_message),
        QueueHandler('info-request', on_message)
    ]
    BillingConsumers(queue_handlers).run()

if __name__ == '__main__':
    run()
