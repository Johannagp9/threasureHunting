import datetime
import cloudinary.uploader

from django.shortcuts import render, redirect
from datetime import datetime

from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from client.services import service
from client.services.user_service import *
from client.services.chat_service import *
from client.services.game_service import *
from client.services.treasure_service import *
from django.http import HttpResponseRedirect
from .forms import CreateGameForm, GameInformationForm
import folium


from django.shortcuts import render

# Create your views here.
##TEMPLATES
LOGIN_TEMPLATE = "login.html"
REGISTER_USER_TEMPLATE = "register.html"
SHOW_GAME_TEMPLATE = "show-game.html"
SHOW_TREASURE_TEMPLATE = "show-treasure.html"
MAP_TEMPLATE = "map.html"
GAMES_TEMPLATE = "games.html"
CREATE_GAME_TEMPLATE = "create_game.html"
GAME_INFORMATION_TEMPLATE = "game_information.html"



# Create your views here.
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def login(request):
    return render(request, LOGIN_TEMPLATE)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def display_games(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    games_list = get_all_games(token)
    for game in games_list:
        if game["winner"]:
            game["winner_name"] = get_user(game['winner'], token)["name"]

    return render(request, GAMES_TEMPLATE, {
                  "games_list": paginate(request, games_list, 8)
    })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def my_games(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    params = {'user': user['id']}
    games_list = get_all_games(token, params)
    if games_list is None:
        games_list = []
    for game in games_list:
        if game["winner"]:
            game["winner_name"] = get_user(game['winner'], token)["name"]

    return render(request, GAMES_TEMPLATE, {
                  "games_list": paginate(request, games_list, 8)
    })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def created_games(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    token = user['google_id']
    params = {'creator': user['id']}
    games_list = get_all_games(token, params)
    if games_list is None:
        games_list = []
    for game in games_list:
        if game["winner"]:
            game["winner_name"] = get_user(game['winner'], token)["name"]

    return render(request, GAMES_TEMPLATE, {
                  "games_list": paginate(request, games_list, 8)
    })


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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
            return redirect("/games")
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
        return redirect("/games")
    else:
        messages.error(request, "An error has occurred.")
        return render(request, REGISTER_USER_TEMPLATE)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def logout(request):
    request.session['user'] = None
    return render(request, LOGIN_TEMPLATE)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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
    chat = {"user1": user['id'], "user2": request.POST.get("receiver"),
            "messages": [{"content": request.POST.get("message"), "date_sent": datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%S"), "sender": user['id'], "read": False}]}

    create_chat(chat, token)

    return redirect("show_chats")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def show_game(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    game = get_game(id, user['google_id'])

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
    dict = {"game": game, "user": user, "maps": service.get_map(game['location'], treasures, show_treasures),
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
    if game['restart_date'] is None:
        del game['restart_date']
    print(game)
    response = update_game(id, game, user['google_id'])
    check_response(request, response)
    if response:
        messages.success(request, "You signed up for the game!")
    else:
        messages.error(request, "An error has occurred, you have not signed up for the game.")
    return redirect("/game/" + id)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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

    dict = {"treasure": treasure, "user": user, "maps": service.get_map(treasure['coordinates'], [], show_instances),
            'instances_validated': instances_validated, "instances_pending": instances_pending,
            'instance_user': instance_user, 'show_instances': show_instances, 'id_creator': id_creator}
    return render(request, SHOW_TREASURE_TEMPLATE, dict)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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

    games = get_game_by_treasure(treasure['id'], user['google_id'])
    check_response(request, games)
    game = games[0]
    num_treasures = len(game['treasures'])
    num_treasures_found = 0
    for game_treasure in game['treasures']:
        treasure = get_treasure(game_treasure, user['google_id'])
        check_response(request, treasure)
        treasure_instance = [instance for instance in treasure['instances'] if instance['user'] == id_user]
        if len(treasure_instance):
            num_treasures_found += 1

    if num_treasures == num_treasures_found:
        game['winner'] = id_user
        i = 0
        while game['instances'][i]['user'] != id_user and i < len(game['instances']):
            i += 1
        game['instances'][i]['complete'] = True

        user = get_user(id_user, user['google_id'])
        check_response(request, user)
        game['active'] = False
        response = update_game(game['id'], game, user['google_id'])
        check_response(request, response)
        if response:
            messages.success(request, "Game is over, the winner is " + user['name'] + " !")
        else:
            messages.error(request, "An error has occurred.")
    if response:
        messages.success(request, "You have validated the treasure!")
    else:
        messages.error(request, "An error has occurred, your validation has not been sent.")
    return redirect("/treasure/" + id + '/' + id_creator)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
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
    })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def store_image_treasure(file):
    if len(file) > 0:
        result = cloudinary.uploader.upload(file, transformation=[
            {'width': 500, 'crop': 'scale', }])
        image_url = result["url"]
        return image_url

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def new_game(request):
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
            data['location'] = request.POST.get('coordinates')
            data['height'] = int(request.POST.get('height'))/360
            data['width'] = int(request.POST.get('width'))/360
            data['active'] = True
            data['treasures'] = []
            request.session['game'] = data
            return HttpResponseRedirect("/create/information")
    else:
        form = CreateGameForm()

    return render(request, CREATE_GAME_TEMPLATE,{
         "form": form,
        })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def game_information(request):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    print(request.method)
    if request.method == "POST":
        form_information = GameInformationForm(request.POST, request.FILES)
        print(form_information)
        print(form_information.is_valid())
        if form_information.is_valid():
            game = request.session.get("game")
            if game :
                location = request.POST.get('location')
                picture = store_image_treasure(request.FILES["picture"])
                clue = form_information.cleaned_data["clue"]
                response = create_treasure({
                    'location':location,
                    'picture': picture,
                    'clue':clue
                }, user['google_id'])
                if response:
                   print("TESORO CREADO JEJE")
                   print(response)
                   game['treasures'].append(response)
                request.session['game'] = game
            else:
                messages.error(request, "An error has occurred.")
            if 'another' in request.POST:
                return HttpResponseRedirect("/create/information")
            if 'create' in request.POST:
                response = create_game(game,user['google_id'])
                request.session['game'] = None
                if not response:
                    messages.error(request, "An error has occurred.")
                else:
                      messages.success(request, "Game has been created!")
                return HttpResponseRedirect("/home")

    else:
        form_information = GameInformationForm()

    return render(request, GAME_INFORMATION_TEMPLATE, {
        "form_information": form_information,
    })

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def get_area(coordinates, height, width):
    maps = folium.Map(location=coordinates, zoom_start=10)
    points = [[coordinates[0]-width/2,coordinates[1]-height/2],[coordinates[0]+width/2,coordinates[1]+height/2],[coordinates[0]-width/2,coordinates[1]-height/2 ],[coordinates[0]+width/2,coordinates[1]+height/2]]
    folium.Rectangle(bounds=points, color='#ff7800', fill=True, fill_color='#ffff00', fill_opacity=0.2).add_to(maps)
    maps = maps._repr_html_()
    return maps 

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def get_map(treasure_coordinates, game):
    coordinates = get_coordinates(game['location'])
    maps = folium.Map(location=(coordinates['lat'], coordinates['long']), zoom_start=10)
    points = [[coordinates['lat']-int(game['height'])/2,coordinates['long']-int(game['width'])/2],[coordinates['lat']+int(game['height'])/2,coordinates['long']+int(game['width'])/2],[coordinates['lat']-int(game['height'])/2,coordinates['long']-int(game['width'])/2 ],[coordinates['lat']+int(game['height'])/2,coordinates['long']+int(game['width'])/2]]
    folium.Rectangle(bounds=points, color='#ff7800', fill=True, fill_color='#ffff00', fill_opacity=0.2).add_to(maps)
    folium.Marker(
                location=treasure_coordinates,
                radius=8,
                icon=folium.Icon(color="red"),
        ).add_to(maps)
    for treasure in game['treasures']:
        coordinates_dict = get_coordinates(treasure['location'])
        coordinates = (coordinates_dict['lat'], coordinates_dict['long'])
        folium.Marker(
                location=coordinates,
                radius=8,
                icon=folium.Icon(color="red"),
        ).add_to(maps)
    maps = maps._repr_html_()
    return maps

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def game_area(request):
    print(request.POST.get('location'))
    coordinates = get_coordinates(request.POST.get('location'))
    width = request.POST.get('width')
    height = request.POST.get('height')
    if (len(coordinates) == 2):
        maps = get_area((coordinates['lat'], coordinates['long']),int(height)/360,int(width)/360)
        return render(request, MAP_TEMPLATE, {"maps":maps})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def maps(request):
    coordinates = get_coordinates(request.POST.get('location'))
    if (len(coordinates) == 2):
        maps = get_map((coordinates['lat'], coordinates['long']),request.session.get("game"))
        return render(request, MAP_TEMPLATE, {"maps":maps})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def user_map(request):
    post_dict = request.POST.dict()
    coordinates = list(post_dict.values())
    maps = folium.Map(location=coordinates, zoom_start=10)
    folium.Marker(
        location=coordinates
    ).add_to(maps)
    maps = maps._repr_html_()
    return render(request, MAP_TEMPLATE, {"maps": maps})