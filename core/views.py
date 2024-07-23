from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # insert "permission_classes = [IsAuthenticated]"" in the class to require authentication
from .serializers import (UserGetSerializer,
                          UserCreateSerializer,
                          UserUpdateSerializer,
                          ShoppingListGetSerializer,
                          ShoppingListCreateSerializer,
                          ShoppingListUpdateSerializer)
from .models import User, ShoppingList
from rest_framework.views import APIView


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return []

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserGetSerializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):  # to delete all users
        User.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        serializer = UserGetSerializer(user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ShoppingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListCreateSerializer

    def get(self, request, *args, **kwargs):
        shopping_lists = ShoppingList.objects.all()
        serializer = ShoppingListGetSerializer(shopping_lists, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ShoppingListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListUpdateSerializer
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        shopping_list = ShoppingList.objects.get(pk=kwargs["pk"])
        serializer = ShoppingListGetSerializer(shopping_list)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        shopping_list = ShoppingList.objects.get(pk=kwargs["pk"])
        serializer = ShoppingListUpdateSerializer(shopping_list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
