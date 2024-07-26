from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User as AuthUserModel
from knox.models import AuthToken
from .models import Account, List
from .serializers import AccountSerializer, ListSerializer, AuthUserSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from . import utils


class RegisterUserView(generics.CreateAPIView):
    serializer_class = AuthUserSerializer

    def post(self, request, *args, **kwargs):
        """Creates a new user and associated account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": AuthUserSerializer(user, context=self.get_serializer_context()).data,
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
        account = self.get_object()
        user = self.request.user
        utils.update_account(account, serializer, user)
    
    def perform_destroy(self, instance):
        """Override perform_destroy to also delete the associated user."""
        account = utils.delete_account(instance, self.request.user)
        super().perform_destroy(account)
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
        account = self.request.user.account
        utils.create_list(serializer, account)

class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Override perform_update to enforce list update rules."""
        list_instance = self.get_object()
        account = self.request.user.account
        utils.update_list(list_instance, account, serializer)
    
    def perform_destroy(self, instance):
        """Override perform_destroy to enforce list deletion rules."""
        account = self.request.user.account
        utils.delete_list(instance, account)
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
