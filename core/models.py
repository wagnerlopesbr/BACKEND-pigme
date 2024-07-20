from django.db import models
from django.contrib.auth import models as auth_models


class User(models.Model):
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=50, blank=False)
    zip_code = models.CharField(max_length=50, blank=False)
    owner = models.ForeignKey(auth_models.User, related_name="users", on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class List(models.Model):
    title = models.CharField(max_length=150, blank=False)
    user = models.ForeignKey(User, related_name="lists", on_delete=models.CASCADE)
    products = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
