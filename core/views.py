from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User as AuthUserModel
from knox.models import AuthToken
from .models import Account, List
from .serializers import AccountSerializer, ListSerializer, AuthUserSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class RegisterUserView(generics.CreateAPIView):
    serializer_class = AuthUserSerializer

    def post(self, request, *args, **kwargs):
        """Creates a new user and associated account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = AuthToken.objects.create(user)[1]
        return Response({
            "user": AuthUserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
        })


class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete an Account."""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Returns the currently logged-in user's account."""
        return self.request.user.account
    
    def perform_destroy(self, instance):
        """Override perform_destroy to also delete the associated user."""
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this account.")
        instance.user.delete()
        super().perform_destroy(instance)
        return Response({"message": "Account and user deleted."})


class AccountListsView(generics.ListAPIView):
    """View to list all lists associated with the currently logged-in user's account."""
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns only lists associated with the currently logged-in user's account."""
        return List.objects.filter(account=self.request.user.account)


class ListCreateView(generics.CreateAPIView):
    """View to create a new list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Associates the list with the currently logged-in user's account."""
        serializer.save(account=self.request.user.account)


class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns only lists associated with the currently logged-in user's account."""
        return List.objects.filter(account=self.request.user.account)


class LoginView(generics.GenericAPIView):
    """View to log in a user."""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """Logs in a user and returns an authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = AuthToken.objects.create(user)[1]
        return Response({
            "user": AuthUserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
        })
