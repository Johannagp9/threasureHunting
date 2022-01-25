from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import CreateGameForm


# Create your views here.
##TEMPLATES
LOGIN_TEMPLATE = "login.html"


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)

def create_game(request):
    if request.method == "POST":
        form = CreateGameForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponseRedirect("/create/information")

    else:
        form = CreateGameForm()

    return render(request, "client/create_game.html",{
         "form": form,
        })

def game_information(request):
    return render(request, "client/game_information.html")