from django.shortcuts import render

# Create your views here.
##TEMPLATES
LOGIN_TEMPLATE = "login.html"
GAMES_TEMPLATE = "games.html"


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)

def display_games(request):
    gamesList = [1, 2, 3, 4, 5, 6, 7]
    return render(request, GAMES_TEMPLATE, {
        "games_list" : gamesList
    })
