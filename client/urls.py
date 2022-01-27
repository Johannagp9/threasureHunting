from django.urls import path

from client import views

urlpatterns = [

path('auth/', views.auth_user, name='auth'),
path('register/', views.auth_user, name='register'),
path('', views.index, name='home'),
]