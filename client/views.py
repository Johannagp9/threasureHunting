import datetime
import cloudinary.uploader

from django.shortcuts import render, redirect
from datetime import datetime

from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from client import services
from client.services.user_service import *
from client.services.chat_service import *
from client.services.game_service import *
from client.services.treasure_service import *
from django.http import HttpResponseRedirect
from .forms import CreateGameForm, GameInformationForm
import folium


LOGIN_TEMPLATE = "login.html"
REGISTER_USER_TEMPLATE = "register.html"
SHOW_GAME_TEMPLATE = "show-game.html"
SHOW_TREASURE_TEMPLATE = "show-treasure.html"
MAP_TEMPLATE = "map.html"

json_data = {
    "treasure_information":[

    ]
}


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)

@csrf_exempt
def auth_user(request):
    id_token = request.POST.get('token')
    idinfo = authenticate_user(id_token)
    if idinfo is not None:
        user = get_user_by_token(idinfo['sub'])
        check_response(request, user)
        if user is None:
            request.session['token'] = idinfo
            return render(request, REGISTER_USER_TEMPLATE)
        else:
            request.session['user'] = user[0]
            return redirect("/home")
    else:
        return render(request, LOGIN_TEMPLATE)

def check_response(request, response):
    if isinstance(response, HttpResponse):
        if response.status_code == 401:
            return render(request, LOGIN_TEMPLATE)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def save_user(request):

    idinfo = request.session.get("token")
    user = {"google_id": idinfo['sub'],
               "name": request.POST.get("name"),
               "email": idinfo['email'],
                "birth_date": request.POST.get("date"),
               "admin": idinfo['email'] == 'pruebaparaingweb@gmail.com'}

    response = create_user(user, idinfo['sub'])
    if response:
        messages.success(request, "You just signed up for the treasure hunt!")
        users = get_user_by_token(idinfo['sub'])
        request.session['user'] = users[0]
        return redirect("/home")
    else:
        messages.error(request, "An error has occurred.")
        return render(request, REGISTER_USER_TEMPLATE)


@csrf_exempt
def logout(request):
    request.session['user'] = None
    return render(request, LOGIN_TEMPLATE)



@csrf_exempt
def index(request):
    return render(request, "base.html")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def show_chats(request):

    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    chats = get_all_chats(token, {"user": user['id']})
    if chats is None:
        chats = []
    else:
        for chat in chats:
            user1 = get_user(chat['user1'], token)
            chat['user1'] = {"id": user1['id'], "name": user1['name']}
            user2 = get_user(chat['user2'], token)
            chat['user2'] = {"id": user2['id'], "name": user2['name']}
            chat['without_read'] = len([ message for message in chat['messages'] if message['sender']!=user["id"] and  message["read"]==False])
        chats = chats
    users = get_all_users(token)
    return render(request, "chats.html",
    {
        "chats": chats,
        "users": users,
        "user": user["id"],
    })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def new_message(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    chat = get_chat(request.POST.get('chat'), user['google_id'])
    chat['messages'].append(
        {"content": request.POST.get('message'), "date_sent": datetime.today().strftime("%Y-%m-%dT%H:%M:%S"),
         "sender":  user['id'], "read":False})

    update_chat(chat['id'], chat, user['google_id'])

    return redirect("/chat/show/" + chat['id'])

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def new_chat(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    print("Sending message")
    chat = {"user1": user['id'], "user2": request.POST.get("receiver"),
            "messages": [{"content": request.POST.get("message"), "date_sent": datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%S"), "sender": user['id'], "read": False}]}

    create_chat(chat, token)

    return redirect("show_chats")



def show_game(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    game = get_game('61f5a32d75143a90d5ebad66', user['google_id'])

    check_response(request, game)
    game['creator'] = get_user(game['creator'], user['google_id'])
    check_response(request, game['creator'])

    if game['winner'] is not None:
        game['winner'] = get_user(game['winner'], user['google_id'])
        check_response(request, game['winner'])

    can_not_signup = False

    if game['instances'] is not None and len(game['instances']):
        game['players'] = []
        for instance in game['instances']:
            can_not_signup = instance['user'] == user['id']
            instance['user'] = get_user(instance['user'], user['google_id'])
            game['players'].append(instance['user'])

    treasures = []

    if game['treasures'] is not None and len(game['treasures']):
        for treasure in game['treasures']:
            treasure = get_treasure(treasure, user['google_id'])
            check_response(request, treasure)
            treasures.append(treasure)


    show_treasures = user['admin'] or user['id'] == game['creator']['id']
    dict = {"game": game, "user": user, "maps": get_map(game['location'], treasures, show_treasures),
            'canNotSignup': can_not_signup, "show_treasures": show_treasures, 'treasures': treasures}
    return render(request, SHOW_GAME_TEMPLATE, dict)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def restart_game(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    game = get_game(id, user['google_id'])
    if game['instances'] is not None and len(game['instances']):
        for instance in game['instances']:
            instance['complete'] = False

    if game['treasures'] is not None and len(game['treasures']):
        for treasure in game['treasures']:
            treasure = get_treasure(treasure, user['google_id'])
            check_response(request, treasure)
            if treasure['instances'] is not None and len(treasure['instances']):
                for instance in treasure['instances']:
                    response = delete_treasure(instance['id'], user['google_id'])
                    check_response(request, response)
                treasure['instances'] = []
                response = update_treasure(id, treasure, user['google_id'])
                check_response(request, response)

    game['restart_date'] = datetime.datetime.utcnow().date().today().__str__()
    game['winner'] = None
    response = update_game(id, game, user['google_id'])
    check_response(request, response)
    if response:
        messages.success(request, "Game has been reset!")
    else:
        messages.error(request, "An error has occurred, your game has not been restarted.")
    return redirect("/game/" + id)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def signup_game(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    game = get_game(id, user['google_id'])
    if game['instances'] is None:
        game['instances'] = []

    instance = {}
    instance['complete'] = False
    instance['user'] = user['id']
    game['instances'].append(instance)
    response = update_game(id, game, user['google_id'])
    check_response(request, response)
    if response:
        messages.success(request, "You signed up for the game!")
    else:
        messages.error(request, "An error has occurred, you have not signed up for the game.")
    return redirect("/game/" + id)


def show_treasure(request, id, id_creator):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)

    treasure = get_treasure(id, user['google_id'])
    check_response(request, treasure)

    instance_user = None

    if treasure['instances'] is not None and len(treasure['instances']):
        for instance in treasure['instances']:
            instance['user'] = get_user(instance['user'], user['google_id'])
            check_response(request, instance['user'])
            if instance['user']['id'] == user['id']:
                instance_user = instance

    instances_validated = [instance for instance in treasure['instances'] if instance['validated']]
    instances_pending = [instance for instance in treasure['instances'] if not instance['validated'] and instance['picture_found'] is not None]



    show_instances = user['admin'] or user['id'] == id_creator

    dict = {"treasure": treasure, "user": user, "maps": get_map(treasure['coordinates'], [], show_instances),
            'instances_validated': instances_validated, "instances_pending": instances_pending,
            'instance_user': instance_user, 'show_instances': show_instances, 'id_creator': id_creator}
    return render(request, SHOW_TREASURE_TEMPLATE, dict)


def check_winner(request, treasure, id_user, token):
    games = get_game_by_treasure(treasure, token)
    check_response(request, games)
    game = games[0]
    is_winner = True
    i=0
    while is_winner and i < len(game['treasures']):
        treasure = get_treasure(game['treasures'][i], token)
        check_response(request, treasure)
        treasure_instance = [instance for instance in treasure['instances'] if instance['user'] == id_user]
        is_winner = len(treasure_instance) == 0
        i += 1

    if is_winner:
        game['winner'] = id_user
        i = 0
        while game['instances'][i]['user'] != id_user and i < len(game['instances']):
            i += 1
        game['instances'][i]['complete'] = True

        user = get_user(id_user, token)
        check_response(request, user)

        response = update_game(game['id'], game, token)
        check_response(request, response)
        if response:
            messages.success(request, "Game is over, the winner is "+user['name']+" !")
        else:
            messages.error(request, "An error has occurred.")
    pass


def validate_treasure(request, id, id_user, id_creator):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)

    treasure = get_treasure(id, user['google_id'])
    check_response(request, treasure)

    instance = [instance for instance in treasure['instances'] if instance['user'] == id_user][0]
    instance['validated'] = True

    response = update_treasure(id, treasure, user['google_id'])
    check_response(request, response)
    check_winner(request, treasure['id'], id_user, user['google_id'])
    if response:
        messages.success(request, "You have validated the treasure!")
    else:
        messages.error(request, "An error has occurred, your validation has not been sent.")
    return redirect("/treasure/" + id + '/' + id_creator)


def create_instance_treasure(request, id, id_creator):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)

    treasure = get_treasure(id, user['google_id'])
    check_response(request, treasure)

    img_url = None
    if len(request.FILES) > 0:
        file = request.FILES['image']
        result = cloudinary.uploader.upload(file, transformation=[
            {'width': 500, 'crop': 'scale', }])
        img_url = result["url"]

    instance = {"picture_found": img_url, "user": user['id'], "validated": False}
    treasure['instances'].append(instance)

    response = update_treasure(id, treasure, user['google_id'])
    check_response(request, response)
    if response:
        messages.success(request, "Treasure has been sent!")
    else:
        messages.error(request, "An error has occurred, your treasure has not been sent.")
    return redirect("/treasure/" + id + '/' + id_creator)


def show_chat(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    chat = get_chat(id,token)
    chat_messages = chat['messages']
    for message in chat['messages']:
        if message['sender']!= user['id'] and not message['read']:
            message['read']=True
    chat['messages'] = chat_messages
    response = update_chat(chat['id'],chat,token)
    if not response:
        messages.error(request, "An error has occurred, try later")
        return redirect('show_chats')
    else:
        user1 = get_user(chat['user1'], token)
        chat['user1'] = {"id": user1['id'], "name": user1['name']}
        user2 = get_user(chat['user2'], token)
        chat['user2'] = {"id": user2['id'], "name": user2['name']}
        return render(request,"show-chat.html",{
        "chat": chat,
        "user": user["id"],
    } )

def store_image_treasure(file):
    if len(file) > 0:
        result = cloudinary.uploader.upload(file, transformation=[
            {'width': 500, 'crop': 'scale', }])
        image_url = result["url"]
        return image_url

def edit_game(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)

    maps = get_map([54.372158,18.638306])
    if request.method == "POST":
        form = CreateGameForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            data['picture'] = store_image_treasure(request.FILES["picture"])
            print(data)
            return HttpResponseRedirect("/create/information")
    else:
        form = CreateGameForm()

    return render(request, "edit_game.html",{
         "form": form,
         "test": range(5),  #number of created Treasures in game
         "title": "Some name",   #Name of the game that user typed
         "treasure_description": "This is example of treasure description to make area look like normal area and some more informations here nothjing important", #it would be good to use here list to refer in templates in each iteration to different text
         "treasure_image": "https://www.polska.travel/images/pl-PL/glowne-miasta/gdansk/gdansk_motlawa_1170.jpg",
         "clue_description": "This is example of treasure description to make area look like normal area and some more informations here nothjing important",
         "map": maps
        })

def create_game(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    if request.method == "POST":
        form = CreateGameForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            data['picture'] = store_image_treasure(request.FILES["picture"])
            data['creator'] = user['id']
            data['coordinates'] = request.POST.get('coordinates')

            print(data)
            return HttpResponseRedirect("/create/information")
    else:
        form = CreateGameForm()

    return render(request, "create_game.html",{
         "form": form,
        })


def game_information(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    print('request')
    print(request.method)
    if request.method == "GET":
        print(request.GET)
        form_information = GameInformationForm()

    # print(response_2_dict(request))

    # if len(json_data["treasure_information"]) > 0:
    #    maps = get_map([json_data["treasure_information"][0]["lat"],json_data["treasure_information"][0]["long"]])
    # else:
    #    maps = get_map([36.72016, -4.42034])

    # for i in range (0,len(json_data["treasure_information"])):
    #  pass
    # maps = get_map([36.72016, -4.42034])
    # print("PRZED form_information->>>>>",request.POST.get('input_localization'))
    elif request.method == "POST":
        # print("form_information->>>>>",request.POST.get('input_localization'))
        # coordinates = _get_coordinates(request.POST['input_localization'])
        # print("game_information",coordinates)
        print(type(request))
        print(request.POST)
        print(type(request.POST))
        form_information = GameInformationForm()

        form_information = GameInformationForm(request.POST, request.FILES)
        if form_information.is_valid():
            # print("VALIDform_information->>>>>",request.POST.get('input_localization'))
            # TODO change with actual_location
            coordinates = get_coordinates(request.POST.get('actual_location'))
            # coordinates = _get_coordinates(request.POST['location'])
            link = store_image_treasure(request.FILES["user_image_2"])
            json_object = {
                "description_treasure": form_information.cleaned_data["description_information"],
                "treasure_image": link,
                "description_clue": form_information.cleaned_data["description_information_clue"],
                "lat": coordinates[0],
                "long": coordinates[1],
            }
            json_data["treasure_information"].append(json_object)
            print(json_data)
            if 'another' in request.POST:
                return HttpResponseRedirect("/create/information")
            if 'create' in request.POST:
                return HttpResponseRedirect("/create")

    else:
        form_information = GameInformationForm()

    print(form_information)

    return render(request, "game_information.html", {
        "form_information": form_information,
    })


def get_map(coordinates):
    maps = folium.Map(location=coordinates, zoom_start=10)
    print("jestem get_map ->",coordinates)
    counter = len(json_data["treasure_information"])+1
    for i in range (0,counter):
        if i == 0:
            folium.Marker(
                location=coordinates
            ).add_to(maps)
            print("go here")
        else:
            folium.Marker(
                location=[json_data["treasure_information"][i-1]["lat"], json_data["treasure_information"][i-1]["long"]]
            ).add_to(maps)
            print("else")

    maps = maps._repr_html_()
    return maps

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def maps(request):
    print("CO TO JEST ->",request)
    coordinates = get_coordinates(request.POST.get('location'))
    if (len(coordinates) == 2):
        maps = get_map((coordinates['lat'], coordinates['long']))
        return render(request, MAP_TEMPLATE, {"maps":maps})


