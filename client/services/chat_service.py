from client.services.service import generate_request, response_2_dict, generate_put, generate_post
from constants import APP_NAME
from route_names import *
from django.urls import reverse

def get_all_chats(token, params={}):
    print("TOKEN")
    print(token)
    url = APP_NAME + reverse(CHATS_SERVER_ROUTE_NAME)
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)


def get_chat(id, token):
    url = APP_NAME + reverse(CHAT_DETAIL_SERVER_ROUTE_NAME, args=(id,)) 
    params = {}
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def update_chat(id, chat, token):
    url = APP_NAME + reverse(CHAT_DETAIL_SERVER_ROUTE_NAME, args=(id,)) 
    response = generate_put(url, chat, token=token)
    return response

def create_chat(chat, token):
    url = APP_NAME + reverse(CHATS_SERVER_ROUTE_NAME)
    response = generate_post(url, chat, token=token)
    return response