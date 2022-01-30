from django.urls import path
from server import views
from route_names import *

urlpatterns = [

    path('auth/', views.auth_user),

    path('users/', views.UserList.as_view(), name=USERS_SERVER_ROUTE_NAME),
    path('users/<str:id>/', views.UserDetail.as_view(), name=USER_DETAIL_SERVER_ROUTE_NAME),
     
    path('games/', views.GameList.as_view(), name=GAMES_SERVER_ROUTE_NAME),
    path('games/<str:id>/', views.GameDetail.as_view(), name=GAME_DETAIL_SERVER_ROUTE_NAME),
  
    path('chats/', views.ChatList.as_view(), name=CHATS_SERVER_ROUTE_NAME),
    path('chats/<str:id>', views.ChatDetail.as_view(), name=CHAT_DETAIL_SERVER_ROUTE_NAME),
]



