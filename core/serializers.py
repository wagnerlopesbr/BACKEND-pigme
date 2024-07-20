from rest_framework import serializers
from .models import User, List
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'title', 'user', 'products']


class UserSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'zip_code', 'lists']


# Auth Session:
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = AuthUser.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        User.objects.create(
            owner=user,
            email=user.email,
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials.")


class UpdateUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    zip_code = serializers.CharField(required=False)

    def update(self, auth_user, validated_data):
        # Update the auth_user instance
        if 'password' in validated_data:
            auth_user.set_password(validated_data['password'])
        auth_user.save()

        try:
            user = User.objects.get(owner=auth_user)
        except User.DoesNotExist:
            raise serializers.ValidationError("User profile not found.")

        # Update the user instance
        if 'name' in validated_data:
            user.name = validated_data['name']
        if 'password' in validated_data:
            user.password = validated_data['password']
        if 'zip_code' in validated_data:
            user.zip_code = validated_data['zip_code']
        user.save()
