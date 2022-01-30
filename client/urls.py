from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_game),
    path("create/information", views.game_information),
    path('auth/', views.auth_user, name='auth'),
    path('register/', views.auth_user, name='register'),
    path('maps/', views.maps, name='maps'),
    path('', views.index, name='home'),
]