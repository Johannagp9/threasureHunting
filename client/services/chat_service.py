from client.services.service import generate_request, response_2_dict, generate_put, generate_post
from constants import APP_NAME
from route_names import *
from django.urls import reverse

def get_all_chats(token, params={}):
    url = APP_NAME + reverse(CHATS_SERVER_ROUTE_NAME)
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

