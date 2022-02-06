from client.services.service import generate_request, response_2_dict, generate_put, generate_post, generate_delete, get_object_id
from constants import APP_NAME
from django.urls import reverse
from route_names import *
import json


def get_all_treasures(token, params={}):
    url = APP_NAME + reverse(TREASURES_SERVER_ROUTE_NAME)
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)


def create_treasure(treasure, token):
    url = APP_NAME + reverse(TREASURES_SERVER_ROUTE_NAME)
    response = generate_post(url, treasure, token=token)
    if response:
        return get_object_id(response)

def get_treasure(id, token):
    url = APP_NAME + reverse(TREASURE_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    params = {}
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def update_treasure(id, treasure, token):
    url = APP_NAME + reverse(TREASURE_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    response = generate_put(url, treasure, token=token)
    return response


def delete_treasure(id, token):
    url = APP_NAME + reverse(TREASURE_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    response = generate_delete(url, token=token)
    return response