import logging

import pika
from django.conf import settings

from .exceptions import ConnectionFailedException, QueueNotDefinedException


logg = logging.getLogger("jusbrasil_challenge.mq_gestor")


class MQManager:
    def __init__(self):
        _settings = settings.MQ_SETTINGS
        self.queue = False
        self.params = pika.ConnectionParameters(
            host=_settings["host"],
            port=_settings["port"],
            credentials=pika.credentials.PlainCredentials(
                _settings["credentials"]["user"],
                _settings["credentials"]["password"],
            ),
        )

        try:
            self.conn = pika.BlockingConnection(parameters=self.params)
            self.channel = self.conn.channel()
        except Exception as e:
            raise ConnectionFailedException(str(e))  # TODO: testar o erro

    def set_queue(self, queue) -> bool:
        if queue == self.queue:
            return

        self.queue = queue
        self.channel.queue_declare(
            queue=self.queue, auto_delete=False, durable=True, exclusive=False
        )

    def send_message(self, message, queue=False):
        queue = self.queue if not queue else queue

        if not queue:
            raise QueueNotDefinedException()

        self.set_queue(queue)

        self.channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(delivery_mode=1),
            mandatory=True,
        )

    def consume(self, callback):
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=callback, auto_ack=False
        )
        logg.info(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def aprove_message(self, method):
        self.channel.basic_ack(method.delivery_tag)

    def reject_message(self, method):
        self.channel.basic_reject(method.delivery_tag)

    def close(self):
        self.conn.close()
