"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import UserViewSet, ListViewSet, RegisterViewSet, LoginViewSet, AuthUserViewSet, UpdateUserViewSet
from knox import views as knox_views


router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"lists", ListViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/auth", include("knox.urls")),
    path("api/auth/register", RegisterViewSet.as_view()),
    path("api/auth/login", LoginViewSet.as_view()),
    path("api/auth/user", AuthUserViewSet.as_view()),
    path("api/auth/logout", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("api/auth/logoutall", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("api/auth/update", UpdateUserViewSet.as_view()),
]
