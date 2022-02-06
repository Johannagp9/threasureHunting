# Treasure Hunting

## Start-Up Guide

1. Install Dependencies
   - $ pip install -r requirements.txt
2. Start Client
   - $ python manage.py runserver
3. Navigate manually through the URLs to see the full functionality
   - path("create", views.create_game),
   - path("create/information", views.game_information),
      - lets you add a treasure
   - path("show_map", views.show_map),
      - provides access to the live location updates
   - path("edit", views.edit_game),
   - path('auth/', views.auth_user, name='auth'),
      - lets you log-in
   - path('register/', views.auth_user, name='register'),
   - path('maps/', views.maps, name='maps'),

