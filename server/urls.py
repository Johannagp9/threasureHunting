from django.urls import path

from server import views

urlpatterns = [
    path('users/', views.UserList.as_view(), name="user"),
    path('users/<str:id>/', views.UserDetail.as_view(), name="user_id"),
    path('auth/', views.auth_user),
]
