from client.services.service import generate_request, response_2_dict, generate_put, generate_post
from constants import APP_NAME
from django.urls import reverse
from route_names import *


def get_all_games(token, params={}):
    url = APP_NAME + reverse(GAMES_SERVER_ROUTE_NAME)
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)


def create_game(game, token):
    url = APP_NAME + reverse(GAMES_SERVER_ROUTE_NAME)
    response = generate_post(url, game, token=token)
    return response

def get_game(id, token):
    url = APP_NAME + reverse(GAME_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    params = {}
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def get_game_by_treasure(id, token):
    url = APP_NAME + reverse(GAME_DETAIL_SERVER_ROUTE_NAME)
    params = {}
    params['treasure'] = id
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def update_game(id, game, token):
    url = APP_NAME + reverse(GAME_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    response = generate_put(url, game, token=token)
    return response



