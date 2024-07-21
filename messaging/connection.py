import pika
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('AMQPURL')
if not url:
    raise ValueError("AMQPURL is not set in environment variables")

def get_connection():
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    return connection

# one-time setup of the exchange and queues
def setup():
    connection = get_connection()
    channel = connection.channel()

    # Declare exchange
    channel.exchange_declare(exchange='core_exchange', exchange_type='direct', durable=True)

    # Declare queues
    channel.queue_declare(queue='user_operations', durable=True)
    channel.queue_declare(queue='list_operations', durable=True)

    # Bind queues to exchange
    channel.queue_bind(exchange='core_exchange', queue='user_operations', routing_key='user_operations')
    channel.queue_bind(exchange='core_exchange', queue='list_operations', routing_key='list_operations')

    connection.close()

if __name__ == "__main__":
    setup()