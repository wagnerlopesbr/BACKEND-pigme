from django.urls import path
from .views import RegisterUserView, AccountDetailView, ListCreateView, ListDetailView, LoginView, AccountListsView, PasswordChangeView
from knox import views as knox_views

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),  # Route to register a new user
    path('login/', LoginView.as_view(), name='login'),  # Route for user login
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),  # Route to logout a user
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),  # Route to logout from all devices
    path('accounts/', AccountDetailView.as_view(), name='account-detail'),  # Route to get or update the current user's account details
    path('accounts/lists/', AccountListsView.as_view(), name='account-lists'),  # Route to get all lists associated with the current user
    path('accounts/password_change/', PasswordChangeView.as_view(), name='account-password-change'),  # Route to change a user's password
    path('lists/', ListCreateView.as_view(), name='list-create'),  # Route to create a new list
    path('lists/<int:pk>/', ListDetailView.as_view(), name='list-detail'),  # Route to get, update, or delete a specific list
]
