import os

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from phone_bills.billingcommon.logging import configure_log

RABBIT_URL = os.getenv('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')
CONNECTION = Connection(RABBIT_URL)


class QueueHandler:
    def __init__(self, exchange_name, routing_key, on_message_callback, content_type='application/json'):
        exchange = self.declare_exchange(exchange_name)
        self.queue = Queue(exchange=exchange, routing_key=routing_key, auto_delete=True)
        self.on_message_callback = on_message_callback
        self.content_type = content_type
        configure_log(self, __name__)

    def declare_exchange(self, exchange_name):
        exchange = Exchange(exchange_name, channel=CONNECTION.channel(), durable=True, type='topic')
        exchange.declare()
        return exchange

    def on_message(self, body, message):
        try:
            self.on_message_callback(body, message)
            message.ack()
        except Exception:
            self.log.exception(f'Error consuming message: {body}')
            message.reject()


class BillingConsumers(ConsumerMixin):
    def __init__(self, queue_handlers):
        self.connection = CONNECTION
        self.queue_handlers = queue_handlers

    def get_consumers(self, Consumer, _):
        for qh in self.queue_handlers:
            yield Consumer(qh.queue,
                           callbacks=[qh.on_message],
                           accept=[qh.content_type])
