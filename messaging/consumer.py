import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import pika
import json
from messaging.connection import get_connection
from core.models import List, Account
from django.contrib.auth.models import User as AuthUser
from core.utils import create_user_and_account, update_account, delete_account, create_list, update_list, delete_list


def callback(ch, method, properties, body):
    print(f" [x] Received message:\n{body}")
    try:
        message = json.loads(body)
        operation = message["operation"]
        data = message["data"]

        if method.routing_key == 'user_operations':
            handle_user_operations(operation, data)
        elif method.routing_key == 'list_operations':
            handle_list_operations(operation, data)
        else:
            print(f"Unknown routing key: {method.routing_key}")
    except json.JSONDecodeError:
        print("Error decoding JSON message")
    except Exception as e:
        print(f"Error handling callback message: {e}")

def handle_user_operations(operation, data):
    try:
        if operation == "create_user":
            create_user_and_account(data['username'], data['email'], data['password'])
        elif operation == "update_user":
            update_user(data)
        elif operation == "delete_user":
            print("Deleting user")
            delete_user(data)
        else:
            print(f"Unknown user operation: {operation}")
    except Exception as e:
        print(f"Error handling user operation: {e}")

def handle_list_operations(operation, data):
    try:
        if operation == "create_list":
            print("Creating list")
            user = AuthUser.objects.get(id=data['account'])
            account = Account.objects.get(user=user)
            create_list(data['serializer'], account)
        elif operation == "update_list":
            print("Updating list")
            update_list(data)
        elif operation == "delete_list":
            print("Deleting list")
            delete_list(data)
        else:
            print(f"Unknown list operation: {operation}")
    except Exception as e:
        print(f"Error handling list operation: {e}")

def update_user(data):
    try:
        auth_user = AuthUser.objects.get(id=data['id'])
        if 'password' in data:
            auth_user.set_password(data['password'])
        if 'username' in data:
            auth_user.username = data['username']
        auth_user.save()
        try:
            account = Account.objects.get(user=auth_user)
            update_account(account, auth_user)
        except Account.DoesNotExist:
            print("Account not found for the user.")
    except AuthUser.DoesNotExist:
        print("AuthUser not found")

def delete_user(data):
    try:
        auth_user = AuthUser.objects.get(id=data['id'])
        try:
            account = Account.objects.get(user=auth_user)
            delete_account(account, auth_user)
        except Account.DoesNotExist:
            pass
        auth_user.delete()
    except AuthUser.DoesNotExist:
        print("AuthUser not found")

def consume():
    try:
        connection = get_connection()
        channel = connection.channel()

        # Declare exchange and queues, and bind them
        channel.exchange_declare(exchange='core_exchange', exchange_type='direct', durable=True)
        channel.queue_declare(queue='user_operations', durable=True)
        channel.queue_declare(queue='list_operations', durable=True)
        
        channel.queue_bind(exchange='core_exchange', queue='user_operations', routing_key='user_operations')
        channel.queue_bind(exchange='core_exchange', queue='list_operations', routing_key='list_operations')

        channel.basic_consume(
            queue='user_operations',
            on_message_callback=callback,
            auto_ack=True
        )
        channel.basic_consume(
            queue='list_operations',
            on_message_callback=callback,
            auto_ack=True
        )
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        connection.close()


if __name__ == '__main__':
    consume()
