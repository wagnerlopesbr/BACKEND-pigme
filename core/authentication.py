from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ObjectDoesNotExist


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = AuthUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return AuthUser.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
