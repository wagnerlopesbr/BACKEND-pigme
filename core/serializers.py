from rest_framework import serializers
from .models import Account, List
from django.contrib.auth.models import User as AuthUserModel
from django.contrib.auth import authenticate
from . import utils
from messaging.producer import publish


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the Auth User model."""
    class Meta:
        model = AuthUserModel
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Creates a new user with hashed password."""
        publish('create_user', 'user_operations', validated_data)
        return validated_data

class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the Account model."""
    user = AuthUserSerializer(required=False)
    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'user', 'zip_code', 'is_active', 'is_premium']
        read_only_fields = ['user']

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    price = serializers.CharField()
    brand = serializers.CharField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        """Validates the product data."""
        required_keys = {"id", "title", "price", "brand", "quantity"}
        actual_keys = set(data.keys())
        
        # Check for missing or extra keys
        if not required_keys.issubset(actual_keys):
            raise serializers.ValidationError("Product data must contain 'id', 'title', 'price', 'brand', and 'quantity'.")
        if actual_keys != required_keys:
            raise serializers.ValidationError("Unexpected keys found in product data.")
        
        # Validate types
        if not isinstance(data["id"], int):
            raise serializers.ValidationError("The 'id' field must be an integer.")
        if not isinstance(data["title"], str):
            raise serializers.ValidationError("The 'title' field must be a string.")
        if not isinstance(data["price"], str):
            raise serializers.ValidationError("The 'price' field must be a string.")
        if not isinstance(data["brand"], str):
            raise serializers.ValidationError("The 'brand' field must be a string.")
        if not isinstance(data["quantity"], int):
            raise serializers.ValidationError("The 'quantity' field must be an integer.")
        
        return data

class ListSerializer(serializers.ModelSerializer):
    """Serializer for the List model."""
    products = ProductSerializer(many=True, required=False)

    class Meta:
        model = List
        fields = ['id', 'title', 'products', 'account']
        extra_kwargs = {'account': {'read_only': True}, 'title': {'required': False}, 'products': {'required': False}}
    
    def validate(self, data):
        """Validates the List object."""
        return super().validate(data)

class LoginSerializer(serializers.Serializer):
    """Serializer for the login view."""
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        """Validates the user credentials."""
        username = data.get('username')
        password = data.get('password')
        user, token = utils.authenticate_and_generate_token(username, password)
        return {'user': user, 'token': token}

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords must match.")
        return data

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect.")
        return old_password
