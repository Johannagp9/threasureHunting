import json
import sys
import math
import requests
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from constants import APP_NAME
import re
from unicodedata import normalize

headers = {'content_type': 'application/json'}


def generate_request_init(url, params={}):

    response = requests.get(url, params=params)
    
    if response.status_code >= 200 and response.status_code < 300:
        return response.json()

def generate_request(url, token, params):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.get(url, params=params, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        return response.json()
    elif response.status_code == 401:
        return response


def response_2_dict(response):
    # No hago get de nada de la response porque lo quiero todo
    json_response = json.dumps(response)
    result = json.loads(json_response)  # String to list
    return result


def generate_post(url, datos, token):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.post(url, json=datos, headers=headers)
    print(response.__dict__)
    return response


def generate_delete(url, token):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.delete(url, headers=headers)
    return response


def generate_put(url, datos, token):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.put(url, json=datos, headers=headers)
    return response


def authenticate_user(id_token):
    # Llamo a la API.
    url = APP_NAME + "/api/auth/"
    params = {'token': id_token}
    header = {'content_type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, params, headers=header)
    if response:
        return response_2_dict(response.json())
    return None


def paginate(request, list, num_pages, page_to_get='page'):
    paginator = Paginator(list, num_pages)
    page = request.GET.get(page_to_get)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    return items


def get_coordinates(location):
    coordinates = cache.get(location)
    if coordinates is None:
        url_location = "https://nominatim.openstreetmap.org/search?q=" + location + "&format=json&addressdetails=1"
        response = generate_request_init(url_location, {})
        if response:
            result = response_2_dict(response)
            if result:
                lat = float(result[0]["lat"])
                long = float(result[0]["lon"])
                dict = {"long": long, "lat": lat}
                cache.set(normalizar(location), dict, 3600)
                return dict
        return None
    return {"long": coordinates['long'], "lat": coordinates['lat']}

def calculate_min_distance(location,graffiti_lat,graffiti_long):
    if location is not None and graffiti_lat is not None and graffiti_long is not None:
        coordinates=get_coordinates(location)
        print("RAIZ" + str(math.sqrt(pow(graffiti_lat-coordinates['lat'],2)+pow(graffiti_long-coordinates['long'],2))))
        print("HOLA "+ str(sys.float_info.max))
        return math.sqrt(pow(graffiti_lat-coordinates['lat'],2)+pow(graffiti_long-coordinates['long'],2))
    return sys.float_info.max

def normalizar(valor):
    valor = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
        normalize( "NFD", valor), 0, re.I
    )

    return normalize("NFC", valor)


