from django.urls import path
from server import views

urlpatterns = [

    path('graffitis/', views.GameList.as_view(), name="games"),
    path('graffitis/<str:id>/', views.GameDetail.as_view(), name="game"),
  
]





