import os
from kombu import Connection, Exchange
from kombu.pools import producers


rabbit_url = os.getenv('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')
connection = Connection(rabbit_url)


class BillingAPIProducer:
    def __init__(self, exchange, routing_key, serializer):
        self.exchange = Exchange(exchange, type='topic')
        self.routing_key = routing_key
        self.serializer = serializer

    def publish(self, payload, headers=None):
        with producers[connection].acquire(block=True, timeout=0.5) as producer:
            producer.publish(
                payload,
                exchange=self.exchange,
                routing_key=self.routing_key,
                declare=[self.exchange],
                serializer=self.serializer,
                headers=headers)


class AmqpExtension:
    def add_producer(self, name, exchange, routing_key, serializer):
        producer = BillingAPIProducer(exchange, routing_key, serializer)
        setattr(self, name, producer)


def configure_producer(app, name, exchange, routing_key, serializer='json'):
    if not hasattr(app, 'amqp'):
        app.amqp = AmqpExtension()
    app.amqp.add_producer(name, exchange, routing_key, serializer)
