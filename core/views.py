from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .models import User, List
from .serializers import UserSerializer, ListSerializer, AuthUserSerializer, RegisterSerializer, LoginSerializer, UpdateUserSerializer
from knox.models import AuthToken


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.none()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return List.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't delete this list.")
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't delete this user.")
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterViewSet(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "username": AuthUserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1],
        })


class LoginViewSet(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        print(user)
        return Response({
            "user": AuthUserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1],
        })


class AuthUserViewSet(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = AuthUserSerializer

    def get_object(self):
        return self.request.user


class UpdateUserViewSet(generics.GenericAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data.get('email')
        new_zip_code = serializer.validated_data.get('zip_code')
        new_password = serializer.validated_data.get('password')
        new_name = serializer.validated_data.get('name')

        if new_password:
            auth_user = request.user
            auth_user.set_password(new_password)
            auth_user.save()
            user = User.objects.get(owner=auth_user)
            user.password = new_password
            user.save()
        if new_name:
            auth_user = request.user
            auth_user.username = new_name
            auth_user.save()
            user = User.objects.get(owner=auth_user)
            user.name = new_name
            user.save()
        if new_zip_code:
            user = User.objects.get(owner=request.user)
            user.zip_code = new_zip_code
            user.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
        })