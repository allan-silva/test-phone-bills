import os

from kombu import Connection, Queue
from kombu.mixins import ConsumerMixin


RABBIT_URL = os.getenv('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')
CONNECTION = Connection(RABBIT_URL)


class QueueHandler:
    def __init__(self, queue_name, on_message_callback, content_type='application/json'):
        self.queue = Queue(queue_name)
        self.on_message_callback = on_message_callback
        self.content_type = content_type

    def on_message(self, body, message):
        self.on_message_callback(body, message)
        message.ack()


class BillingConsumers(ConsumerMixin):
    def __init__(self, queue_handlers):
        self.connection = CONNECTION
        self.queue_handlers = queue_handlers

    def get_consumers(self, Consumer, _):
        for qh in self.queue_handlers:
            yield Consumer(qh.queue,
                           callbacks=[qh.on_message],
                           accept=[qh.content_type])
