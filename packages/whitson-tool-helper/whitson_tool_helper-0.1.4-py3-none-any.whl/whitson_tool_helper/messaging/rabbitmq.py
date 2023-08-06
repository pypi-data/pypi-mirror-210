import pika
import os
from typing import List
import json

from whitson_tool_helper.messaging.helper import check_environment_variables
from whitson_tool_helper.logger import LOGGER


def get_rabbitmq_params():
    check_environment_variables(
        [
            "RABBITMQ_USER",
            "RABBITMQ_PASSWORD",
            "RABBITMQ_HOST",
            "RABBITMQ_PORT",
        ],
    )
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASSWORD"]
    )
    return pika.ConnectionParameters(
        host=os.environ["RABBITMQ_HOST"],
        port=os.environ["RABBITMQ_PORT"],
        credentials=credentials,
    )


class RabbitMQConsumer:
    def __init__(self, process_function):
        self.process_function = process_function

        check_environment_variables(["MESSAGING_SUBSCRIPTION"])
        parameters = get_rabbitmq_params()
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        subscription = os.getenv("MESSAGING_SUBSCRIPTION")
        self.channel.queue_declare(
            queue=subscription,
            durable=True,
            arguments={"x-max-priority": 100, "x-queue-type": "classic"},
        )
        exchange = "engines"
        if subscription.endswith("-calculated"):
            exchange = "clients"

        self.channel.queue_bind(
            queue=subscription, exchange=exchange, routing_key=subscription
        )

        self.channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            if not body or body.decode("utf-8") == "":
                ch.basic_ack(delivery_tag=method.delivery_tag)
                LOGGER.info("Recieved faulty message")
                LOGGER.info("Listening to", method.routing_key, "...")
                return

            msg = json.loads(body.decode("utf-8"))
            process_function(data=msg["data"], meta_data=msg["meta_data"])
            LOGGER.info("  ---  SUCCESS  ---  ")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            LOGGER.info(f"Listening to {method.routing_key} ...")

        self.channel.basic_consume(queue=subscription, on_message_callback=callback)

    def work(self):
        self.channel.start_consuming()


class RabbitMQPublisher:
    def __init__(self, exchange):
        self.parameters = get_rabbitmq_params()
        self.exchange = exchange

    def publish(
        self, topic: str, payload: dict, meta_data: dict = {}, priority: int = 50
    ):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        message = {"data": payload, "meta_data": meta_data}

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=topic,
            body=json.dumps(message).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                priority=priority,
            ),
        )

        connection.close()

    def publish_many(self, payloads: List[dict], meta_data: dict, priority: int = 50):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        for payload in payloads:
            message = {"data": payload, "meta_data": meta_data}

            channel.basic_publish(
                exchange="engines",
                routing_key=self.topic,
                body=json.dumps(message).encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    priority=priority,
                ),
            )

        connection.close()
