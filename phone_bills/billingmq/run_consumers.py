from phone_bills.billingcommon.logging import configure_log
from phone_bills.billingcommon.dispatcher import message_dispatcher
from phone_bills.billingmq.consumer import QueueHandler, BillingConsumers


class Logger:
    pass


logger = Logger()
configure_log(logger, __name__)


def on_message(body, message):
    logger.log.info(f'Consumers setup test.')
    logger.log.info(f'Message: {message}.')
    logger.log.info(f'Payload: {body}.')
    logger.log.info(f'Headers: {message.headers}\nBody: {body}.')


def run():
    queue_handlers = [
        QueueHandler('call-event', message_dispatcher.phone_call),
        QueueHandler('info-request', on_message)
    ]
    BillingConsumers(queue_handlers).run()


if __name__ == '__main__':
    run()
