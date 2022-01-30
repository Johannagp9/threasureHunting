from django.urls import path
from . import views

urlpatterns = [
    path("games", views.display_games, name="display_games"),
]