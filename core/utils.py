from django.contrib.auth.models import User as AuthUserModel
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Account, List
from knox.models import AuthToken


def create_user_and_account(username, email, password):
    """Creates a new user and associated account."""
    if AuthUserModel.objects.filter(email=email).exists():
            raise ValueError({'email': 'Email already exists'})
    str_password = str(password)
    user = AuthUserModel.objects.create_user(username=username,
                                             email=email,
                                             password=str_password)
    Account.objects.create(user=user)
    return user

def create_list(serializer, account):
    """Creates a new list (List) associated with the given account."""
    print(f"Creating list with data: {serializer}")
    current_list_count = List.objects.filter(account=account).count()
    if not account.is_premium and current_list_count >= 3:
        raise PermissionDenied("Free accounts are limited to 3 lists.")
    if account.is_premium and current_list_count >= 10:
        raise PermissionDenied("Premium accounts are limited to 10 lists.")
    products = serializer.get('products')
    if len(products) > 40:
        raise ValidationError("Lists cannot exceed 40 products.")
    return List.objects.create(title=serializer.get('title'), account=account)

def authenticate_and_generate_token(username, password):
    """Authenticates a user and generates an Auth Token"""
    user = authenticate(username=username, password=password)
    if user and user.is_active:
         token = AuthToken.objects.create(user)[1]
         return user, token
    raise ValidationError("Incorrect credentials.")

def update_account(account, serializer, user):
    """Updates an account with the given serializer data."""
    if account.user != user:
        raise PermissionDenied("You do not have permission to update this account.")
    serializer.is_valid(raise_exception=True)
    serializer.save(user=account.user)
    return account

def delete_account(account, user):
    """Deletes an account and associated user."""
    if account.user.id != user.id:
        raise PermissionDenied("You do not have permission to delete this account.")
    account = Account.objects.get(user=user)
    account.user.delete()

def update_list(list_instance, account, serializer):
    """Updates a list with the given serializer data."""
    if list_instance.account.id != account.id:
        print(f"Permission denied: list_instance.account={list_instance.account.id}, account={account.id}")
        raise PermissionDenied("You do not have permission to update this list.")
    serializer.is_valid(raise_exception=True)
    updated_list = serializer.save(account=list_instance.account)
    return updated_list

def delete_list(list_instance, account):
    """Deletes a list."""
    if list_instance.account.id != account.id:
        print(f"Permission denied: list_instance.account={list_instance.account.id}, account={account.id}")
        raise PermissionDenied("You do not have permission to delete this list.")
    list_instance.delete()
    return list_instance
