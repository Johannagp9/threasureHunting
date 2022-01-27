from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import CreateGameForm, GameInformationForm
import folium
from folium.plugins import MousePosition


# Create your views here.
##TEMPLATES
LOGIN_TEMPLATE = "login.html"


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)

def store_image_create(file):
    with open("uploads/image.jpg", "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)

def store_image_treasure(file):
    with open("uploads/treasure.jpg", "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)


def create_game(request):
    if request.method == "POST":
        form = CreateGameForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data)
            store_image_create(request.FILES["user_image"])
            return HttpResponseRedirect("/create/information")

    else:
        form = CreateGameForm()

    return render(request, "client/create_game.html",{
         "form": form,
        })




def game_information(request):

    maps = folium.Map(location=[36.74,-4.46], zoom_start=10)


    popup = folium.LatLngPopup()
    maps.add_child(popup)
    maps.add_child(folium.ClickForMarker(popup="Waypoint"))
    maps = maps._repr_html_()

    #MousePosition().add_to(maps)
    #formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    #MousePosition(
    #    position="topright",
    #    separator=" | ",
    #    empty_string="NaN",
    #    lng_first=True,
    #    num_digits=20,
    #    prefix="Coordinates:",
    #    lat_formatter=formatter,
    #    lng_formatter=formatter,
    #).add_to(maps)
    

    if request.method == "POST":
        print("test")
        form_information = GameInformationForm(request.POST, request.FILES)
        if form_information.is_valid():
            store_image_treasure(request.FILES["user_image_2"])
            print(form_information.cleaned_data)
            return HttpResponseRedirect("/create/information")
    else:
        form_information = GameInformationForm()

    return render(request, "client/game_information.html",{
        "form_information": form_information,
        "maps": maps,
    })