from client.services.service import *
from constants import APP_NAME
from django.urls import reverse
from route_names import *

def get_all_users(token, params={}):
    url = APP_NAME + reverse(USERS_SERVER_ROUTE_NAME)
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def get_user(id, token):
    url = APP_NAME + reverse(USER_DETAIL_SERVER_ROUTE_NAME, args=(id,))
    params = {}
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def get_user_by_token(token):
    url = APP_NAME + reverse(USERS_SERVER_ROUTE_NAME)
    params = {}
    params['google_id'] = token
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def create_user(user, token):
    url = APP_NAME + reverse(USERS_SERVER_ROUTE_NAME)
    response = generate_post(url, user, token=token)
    return response

