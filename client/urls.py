from django.urls import path

from client import views

urlpatterns = [

    path('auth/', views.auth_user, name='auth'),
    path('register/', views.save_user, name='register'),
    path('home/', views.index, name='home'),
    path('game/<str:id>', views.show_game, name='game'),
    path('treasure/<str:id>/<str:id_creator>', views.show_treasure, name='treasure'),
    path('restart_game/<str:id>', views.restart_game, name='restart_game'),
    path('validate_treasure/<str:id>/<str:id_user>/<str:id_creator>', views.validate_treasure, name='validate_treasure'),
    path('create_instance_treasure/<str:id>/<str:id_creator>', views.create_instance_treasure, name='create_instance_treasure'),
    path('logout/', views.logout, name='logout'),
    path('signup_game/<str:id>', views.signup_game, name='signup_game'),
    path('chats/', views.show_chats, name='show_chats'),
    path('chats/new',views.new_chat, name='new_chat'),
    path('message/new',views.new_message, name='new_message'),
    path('chat/show/<str:id>', views.show_chat,name='show_chat' ),
    path("create", views.create_game, name="new_game"),
    path("create/information", views.game_information),
    path('area/', views.game_area, name='game_area'),
    path('maps/', views.maps, name='maps'),

]