from rest_framework import serializers
from .models import Account, List
from django.contrib.auth.models import User as AuthUserModel


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the Auth User model."""
    class Meta:
        model = AuthUserModel
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Creates a new user with hashed password."""
        password = validated_data.pop('password', None)
        if AuthUserModel.objects.filter(email=validated_data.get('email')).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        user = AuthUserModel.objects.create_user(username=validated_data['username'],
                                                 email=validated_data['email'],
                                                 password=password)
        Account.objects.create(user=user)
        return user


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the Account model."""
    class Meta:
        model = Account
        fields = ['id', 'user', 'zip_code', 'is_active', 'is_premium']
        read_only_fields = ['user']

class ListSerializer(serializers.ModelSerializer):
    """Serializer for the List model."""
    class Meta:
        model = List
        fields = ['id', 'title', 'products', 'account']
