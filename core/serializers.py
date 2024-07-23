from rest_framework import serializers
from .models import User, ShoppingList

class ShoppingListGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ["id", "user_id", "title", "products"]
        extra_kwargs = {
            "products": {"read_only": True},
            "user_id": {"read_only": True},
        }

class UserGetSerializer(serializers.ModelSerializer):
    shopping_lists = ShoppingListGetSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "is_premium", "shopping_lists"]
        extra_kwargs = {
            "first_name": {"read_only": True, "required": False},
            "last_name": {"read_only": True, "required": False},
            "email": {"read_only": True, "required": False},
            "is_premium": {"read_only": True, "required": False},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False},
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "password"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": True},
            "password": {"write_only": True, "required": True},
        }


class ShoppingListCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ShoppingList
        fields = ["id", "title", "products", "user_id"]
        extra_kwargs = {
            "products": {"required": False},
            "title": {"required": True},
            "user_id": {"required": True},
        }

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        shopping_list = ShoppingList.objects.create(user_id=user_id, **validated_data)
        return shopping_list


class ShoppingListUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ["id", "title", "products"]
        extra_kwargs = {
            "products": {"required": False},
            "title": {"required": False},
        }
        