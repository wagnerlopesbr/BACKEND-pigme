from rest_framework import serializers
from .models import Account, List
from django.contrib.auth.models import User as AuthUserModel
from django.contrib.auth import authenticate


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
        fields = ['id', 'first_name', 'last_name', 'user', 'zip_code', 'is_active', 'is_premium']
        read_only_fields = ['user']


class ProductSerializer(serializers.Serializer):
    title = serializers.CharField()
    price = serializers.CharField()
    brand = serializers.CharField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        """Validates the product data."""
        required_keys = {"title", "price", "brand", "quantity"}
        actual_keys = set(data.keys())
        
        # Check for missing or extra keys
        if not required_keys.issubset(actual_keys):
            raise serializers.ValidationError("Product data must contain 'title', 'price', 'brand', and 'quantity'.")
        if actual_keys != required_keys:
            raise serializers.ValidationError("Unexpected keys found in product data.")
        
        # Validate types
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
    products = ProductSerializer(many=True)

    class Meta:
        model = List
        fields = ['id', 'title', 'products', 'account']
        extra_kwargs = {'account': {'read_only': True}}
    
    def validate(self, data):
        """Validates the List object."""
        return super().validate(data)


class LoginSerializer(serializers.Serializer):
    """Serializer for the login view."""
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        """Validates the user credentials."""
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
