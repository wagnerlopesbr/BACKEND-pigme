from django.contrib.auth.models import BaseUserManager, User as AuthUserModel
from django.db import models

class AccountManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if AuthUserModel.objects.filter(email=email).exists():
            raise ValueError('A user with this email already exists')
        if AuthUserModel.objects.filter(username=username).exists():
            raise ValueError('A user with this username already exists')
        user = AuthUserModel.objects.create_user(username=username, email=email, password=password)
        account = Account.objects.create(user=user, **extra_fields)
        return account

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username='admin', email=email, password=password, **extra_fields)

class Account(models.Model):
    user = models.OneToOneField(AuthUserModel, on_delete=models.CASCADE, related_name='account', null=True, blank=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    zip_code = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)

    objects = AccountManager()

    def __str__(self):
        return f"{self.user.get_full_name()}. @username: {self.user.username}"

class List(models.Model):
    """Model to represent a shopping list associated with a user."""
    title = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    products = models.JSONField(default=list, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="lists")

    def __str__(self):
        return self.title
