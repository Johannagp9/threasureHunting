from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_game),
    path("create/information", views.game_information),
]