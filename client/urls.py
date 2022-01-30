from django.urls import path

from client import views

urlpatterns = [
    path('auth/', views.auth_user, name='auth'),
    path('register/', views.save_user, name='register'),
    path('home/', views.index, name='home'),
    path('game/<str:id>', views.show_game, name='game'),
    path('restart_game/<str:id>', views.restart_game, name='restart_game'),
    path('logout/', views.logout, name='logout'),
]