# from .connection import get_connection
# from core.models import User, List
# from django.contrib.auth.models import User as AuthUser
# import json

# def callback(ch, method, properties, body):
#     print(f" [x] Received message:\n{body}")
#     message = json.loads(body)
#     operation = message["operation"]
#     data = message["data"]

#     if method.routing_key == 'user_operations':
#         handle_user_operations(operation, data)
#     elif method.routing_key == 'list_operations':
#         handle_list_operations(operation, data)
#     else:
#         print(f"Unknown routing key: {method.routing_key}")

# def handle_user_operations(operation, data):
#     if operation == "create_user":
#         create_user(data)
#     elif operation == "update_user":
#         update_user(data)
#     else:
#         print(f"Unknown user operation: {operation}")

# def handle_list_operations(operation, data):
#     if operation == "create_list":
#         create_list(data)
#     elif operation == "update_list":
#         update_list(data)
#     elif operation == "delete_list":
#         delete_list(data)
#     else:
#         print(f"Unknown list operation: {operation}")

# def create_user(data):
#     auth_user = AuthUser.objects.create_user(
#         username=data['username'],
#         email=data['email'],
#         password=data['password']
#     )
#     User.objects.create(
#         owner=auth_user,
#         email=auth_user.email,
#         password=data['password'],
#         name=data.get('name', ''),
#         zip_code=data.get('zip_code', '')
#     )

# def update_user(data):
#     try:
#         auth_user = AuthUser.objects.get(id=data['auth_user_id'])
#         if 'password' in data:
#             auth_user.set_password(data['password'])
#         if 'username' in data:
#             auth_user.username = data['username']
#         auth_user.save()

#         user = User.objects.get(owner=auth_user)
#         if 'name' in data:
#             user.name = data['name']
#         if 'password' in data:
#             user.password = data['password']
#         if 'zip_code' in data:
#             user.zip_code = data['zip_code']
#         user.save()
#     except AuthUser.DoesNotExist:
#         print("AuthUser not found")
#     except User.DoesNotExist:
#         print("User not found")

# def create_list(data):
#     user = User.objects.get(id=data['user_id'])
#     List.objects.create(
#         user=user,
#         title=data['title'],
#         products=data.get('products', [])
#     )

# def update_list(data):
#     try:
#         list_instance = List.objects.get(id=data['id'])
#         if 'title' in data:
#             list_instance.title = data['title']
#         if 'products' in data:
#             list_instance.products = data['products']
#         list_instance.save()
#     except List.DoesNotExist:
#         print("List not found")

# def delete_list(data):
#     try:
#         list_instance = List.objects.get(id=data['id'])
#         list_instance.delete()
#     except List.DoesNotExist:
#         print("List not found")

# def consume():
#     try:
#         connection = get_connection()
#         channel = connection.channel()
#         # Declare the exchange before consuming messages
#         channel.exchange_declare(exchange='core_exchange', exchange_type='direct', durable=True)
#         channel.queue_declare(queue='user_operations', durable=True)
#         channel.queue_declare(queue='list_operations', durable=True)

#         channel.basic_consume(
#             queue='user_operations',
#             on_message_callback=callback,
#             auto_ack=True
#         )
#         channel.basic_consume(
#             queue='list_operations',
#             on_message_callback=callback,
#             auto_ack=True
#         )
#         print(' [*] Waiting for messages. To exit press CTRL+C')
#         channel.start_consuming()
#     except Exception as e:
#         print(f"Error consuming message: {e}")
#     finally:
#         connection.close()
