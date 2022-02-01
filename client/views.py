import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
##TEMPLATES

from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from client.services.game_service import get_game, update_game
from client.services.service import authenticate_user, get_coordinates, get_map
from client.services.treasure_service import get_treasure, delete_treasure, update_treasure
from client.services.user_service import get_user_by_token, create_user, get_user

LOGIN_TEMPLATE = "login.html"
REGISTER_USER_TEMPLATE = "register.html"
SHOW_GAME_TEMPLATE = "show-game.html"
SHOW_TREASURE_TEMPLATE = "show-treasure.html"


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
def show_game(request, id):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)
    #'61f708570d5c3eb394ba1001'
    game = get_game('61f5a32d75143a90d5ebad66', user['google_id'])
        #get_game(id, user['google_id'])
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
    print(treasures)
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
    print(game)
    response = update_game(id, game, user['google_id'])
    check_response(request, response)
    print(response.__dict__)
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

    instance_user = {}

    if treasure['instances'] is not None and len(treasure['instances']):
        for instance in treasure['instances']:
            instance['user'] = get_user(instance['user'], user['google_id'])
            check_response(request, instance['user'])
            if instance['user']['id'] == user['id']:
                instance_user = instance

    instances_validated = [instance for instance in treasure['instances'] if instance['validated']]
    instances_pending = [instance for instance in treasure['instances'] if not instance['validated'] and instance['picture_found'] is not None]



    show_instances = user['admin'] or user['id'] == id_creator

    print(treasure)
    dict = {"treasure": treasure, "user": user, "maps": get_map(treasure['coordinates'], [], show_instances),
            'instances_validated': instances_validated, "instances_pending": instances_pending,
            'instance_user': instance_user, 'show_instances': show_instances, 'id_creator': id_creator}
    return render(request, SHOW_TREASURE_TEMPLATE, dict)


def validate_treasure(request, id, id_user, id_creator):
    try:
        user = request.session['user']
        if user is None:
            return render(request, LOGIN_TEMPLATE)
    except:
        return render(request, LOGIN_TEMPLATE)

    treasure = get_treasure(id, user['google_id'])
    check_response(request, treasure)

    instance = [instance for instance in treasure['instances'] if instance.user.id == id_user][0]
    instance['validated'] = True

    response = update_treasure(id, treasure, user['google_id'])
    check_response(request, response)
    if response:
        messages.success(request, "Game has been reset!")
    else:
        messages.error(request, "An error has occurred, your game has not been restarted.")
    return redirect("/treasure/" + id + '/' + id_creator)