from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User as AuthUserModel
from knox.models import AuthToken
from .models import Account, List
from .serializers import AccountSerializer, ListSerializer, AuthUserSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

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

        # Check if the user can create more lists
        current_list_count = List.objects.filter(account=account).count()
        if not account.is_premium and current_list_count >= 3:
            raise PermissionDenied("You can only create up to 3 lists as a non-premium user.")

        if account.is_premium and current_list_count >= 10:
            raise PermissionDenied("You can only create up to 10 lists as a premium user.")

        # Check products length
        products = serializer.validated_data.get('products')
        if len(products) > 40:
            raise ValidationError("The list cannot exceed 40 products.")

        serializer.save(account=account)


class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a list (List)."""
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns only lists associated with the currently logged-in user's account."""
        account = self.request.user.account
        if account.is_premium:
            return List.objects.filter(account=account)
        else:
            # When not a premium user, allow access to the first 3 lists
            return List.objects.filter(account=account)[:3]


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
