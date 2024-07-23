from django.urls import path
from . import views


urlpatterns = [
    path("users/", views.UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", views.UserRetrieveUpdateDestroyView.as_view(), name="user-retrieve-update-destroy"),
    path("shopping_lists/", views.ShoppingListCreateView.as_view(), name="shopping_list-list-create"),
    path("shopping_lists/<int:pk>/", views.ShoppingListRetrieveUpdateDestroyView.as_view(), name="shopping_list-retrieve-update-destroy"),
]