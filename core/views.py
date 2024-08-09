from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User as AuthUserModel
from knox.models import AuthToken
from .models import Account, List
from .serializers import AccountSerializer, ListSerializer, AuthUserSerializer, LoginSerializer, PasswordChangeSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from . import utils
from messaging.producer import publish
from django.contrib.auth import update_session_auth_hash


class RegisterUserView(generics.CreateAPIView):
    serializer_class = AuthUserSerializer

    def post(self, request, *args, **kwargs):
        """Creates a new user and associated account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "User created successfully."
        })

class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete an Account."""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Returns the currently logged-in user's account."""
        return self.request.user.account
    
    def perform_update(self, serializer):
        """Override perform_update to prevent changing the user."""
        print("checking if its valid")
        serializer.is_valid(raise_exception=True)
        print("serializer is valid")
        data = serializer.validated_data
        account = self.get_object()
        account_data = {
            'id': account.id,
            'first_name': account.first_name,
            'last_name': account.last_name,
            'zip_code': account.zip_code,
            'is_active': account.is_active,
            'is_premium': account.is_premium
        }
        user = self.request.user
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        publish('update_user', 'user_operations', {'account': account_data, 'serializer': data, 'user': user_data})
    
    def perform_destroy(self, instance):
        """Override perform_destroy to also delete the associated user."""
        account = self.get_object()
        account_data = {
            'id': account.id
        }
        user = self.request.user
        user_data = {
            'id': user.id
        }
        publish('delete_user', 'user_operations', {'account': account_data, 'user': user_data})
        return Response({"message": "Account and user deleted."})

class AccountListsView(generics.ListAPIView):
    """View to list all lists associated with the currently logged-in user's account."""
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns only lists associated with the currently logged-in user's account."""
        account = self.request.user.account
        if account.is_premium:
            return List.objects.filter(account=account)
        else:
            return List.objects.filter(account=account)[:3]

class ListCreateView(generics.CreateAPIView):
    """View to create a new list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Associates the list with the currently logged-in user's account and enforces list creation rules."""
        data = {'serializer': serializer.validated_data, 'account': self.request.user.account.user_id}
        publish('create_list', 'list_operations', data)

class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Override perform_update to enforce list update rules."""
        list_instance = self.get_object()
        list_instance_data = {
            'id': list_instance.id,
            'title': list_instance.title,
            'products': list_instance.products,
            'account': list_instance.account.id
        }
        account = self.request.user.account
        account_data = {
            'id': account.id
        }
        publish('update_list', 'list_operations', {
            'list_instance': list_instance_data,
            'account': account_data,
            'serializer': serializer.validated_data
        })
    
    def perform_destroy(self, instance):
        """Override perform_destroy to enforce list deletion rules."""
        list_instance = self.get_object()
        list_instance_data = {
            'id': list_instance.id,
            'title': list_instance.title,
            'products': list_instance.products,
            'account': list_instance.account.id
        }
        account = self.request.user.account
        account_data = {
            'id': account.id
        }
        publish('delete_list', 'list_operations', {'list_instance': list_instance_data, 'account': account_data})
        return Response({"message": "List deleted."})

class LoginView(generics.GenericAPIView):
    """View to log in a user."""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """Logs in a user and returns an authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        return Response({
            "user": AuthUserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
        })

class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        return Response({"message": "Password changed successfully."})
