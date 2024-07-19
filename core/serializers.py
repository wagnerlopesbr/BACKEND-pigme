from rest_framework import serializers
from .models import User, List


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'title', 'user', 'products']


class UserSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'zip_code', 'lists']
