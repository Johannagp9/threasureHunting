from client.services.service import *
from constants import APP_NAME
from django.urls import reverse


def get_all_users(token, params={}):
    # Llamo a la API.
    url = APP_NAME + reverse("user")
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def get_user(id, token):
    url = APP_NAME + reverse('user_id', args=(id,))
    params = {}
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def get_user_by_token(token):
    url = APP_NAME + reverse("user")
    params = {}
    params['google_id'] = token
    response = generate_request(url, token=token, params=params)
    if response:
        return response_2_dict(response)

def create_user(user, token):
    url = APP_NAME + reverse("user")
    response = generate_post(url, user, token=token)
    return response

