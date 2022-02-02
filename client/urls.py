from django.urls import path

from client import views

urlpatterns = [

path('auth/', views.auth_user, name='auth'),
path('register/', views.save_user, name='register'),
path('home/', views.index, name='home'),
path('chats/', views.show_chats, name='show_chats'),
]