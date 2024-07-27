from .connection import get_connection
import json
import pika


def publish(operation, routing_key, data):
    try:
        connection = get_connection()
        channel = connection.channel()
        # Declare the exchange before using it
        channel.exchange_declare(
            exchange="core_exchange", exchange_type="direct", durable=True
        )

        message = json.dumps({"operation": operation, "data": data})
        channel.basic_publish(
            exchange="core_exchange",
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
        )
    except Exception as e:
        print(f"Error publishing message: {e}")
    finally:
        connection.close()
