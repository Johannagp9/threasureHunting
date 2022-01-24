from django.urls import path
from server import views

urlpatterns = [

    path('auth/', views.auth_user),

    path('users/', views.UserList.as_view(), name="user"),
    path('users/<str:id>/', views.UserDetail.as_view(), name="user_id"),
     
    path('graffitis/', views.GameList.as_view(), name="games"),
    path('graffitis/<str:id>/', views.GameDetail.as_view(), name="game"),
  
]



