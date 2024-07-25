from django.urls import path
from .views import RegisterUserView, AccountDetailView, ListCreateView, ListDetailView, DeleteUserView
from knox import views as knox_views

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),  # Route to register a new user
    path('delete/<int:pk>/', DeleteUserView.as_view(), name='delete-user'),  # Route to delete a user
    path('login/', knox_views.LoginView.as_view(), name='knox_login'),  # Route for user login
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),  # Route to logout a user
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),  # Route to logout from all devices
    path('accounts/', AccountDetailView.as_view(), name='account-detail'),  # Route to get or update the current user's account details
    path('lists/', ListCreateView.as_view(), name='list-create'),  # Route to create a new list
    path('lists/<int:pk>/', ListDetailView.as_view(), name='list-detail'),  # Route to get, update, or delete a specific list
]
