from django.urls import path

from client import views

urlpatterns = [

path('auth/', views.auth_user, name='auth'),
path('register/', views.save_user, name='register'),
path('home/', views.index, name='home'),
path('chats/', views.show_chats, name='show_chats'),
path('chats/new',views.new_chat, name='new_chat'),
path('message/new',views.new_message, name='new_message')

]