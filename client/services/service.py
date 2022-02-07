import json
import math
import re
import sys

import folium
import requests
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from unicodedata import normalize

from constants import APP_NAME

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
    json_response = json.dumps(response)
    result = json.loads(json_response)
    return result


def generate_post(url, datos, token):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.post(url, json=datos, headers=headers)
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


def generate_delete(url, token):
    try:
        headers['Authorization'] = token
    except KeyError:
        return HttpResponse('Unauthorized', status=401)
    response = requests.delete(url, headers=headers)
    return response


def get_object_id(response):
    return json.loads(response.text)['id']


def authenticate_user(id_token):
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


def get_normalization(valor):
    valor = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", valor), 0, re.I
    )

    return normalize("NFC", valor)


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
                cache.set(get_normalization(location), dict, 3600)
                return dict
        return None
    return {"long": coordinates['long'], "lat": coordinates['lat']}


def calculate_min_distance(location, graffiti_lat, graffiti_long):
    if location is not None and graffiti_lat is not None and graffiti_long is not None:
        coordinates = get_coordinates(location)
        return math.sqrt(pow(graffiti_lat - coordinates['lat'], 2) + pow(graffiti_long - coordinates['long'], 2))
    return sys.float_info.max


def get_map(location, treasures, show_treasures):
    coordinates_dict = get_coordinates(location)
    coordinates = (coordinates_dict['lat'], coordinates_dict['long'])
    maps = folium.Map(location=coordinates, zoom_start=10)
    folium.Marker(
        location=coordinates
    ).add_to(maps)
    if show_treasures:
        for treasure in treasures:
            coordinates_dict = get_coordinates(treasure['coordinates'])
            coordinates = (coordinates_dict['lat'], coordinates_dict['long'])
            folium.Marker(
                location=coordinates,
                radius=8,
                icon=folium.Icon(color="red"),
                popup='Clue: ' + treasure['clue']
            ).add_to(maps)
    maps = maps._repr_html_()
    return maps


def get_map_area(location, width, height, treasures, show_treasures):
    coordinates_dict = get_coordinates(location)
    coordinates = (coordinates_dict['lat'], coordinates_dict['long'])
    maps = folium.Map(location=coordinates, zoom_start=10)
    if width and height:
        points = [[coordinates[0] - width / 2, coordinates[1] - height / 2],
                  [coordinates[0] + width / 2, coordinates[1] + height / 2],
                  [coordinates[0] - width / 2, coordinates[1] - height / 2],
                  [coordinates[0] + width / 2, coordinates[1] + height / 2]]
        folium.Rectangle(bounds=points, color='#ff7800', fill=True, fill_color='#ffff00', fill_opacity=0.2).add_to(maps)
    else:
        folium.Marker(
            location=coordinates
        ).add_to(maps)
    if show_treasures:
        for treasure in treasures:
            coordinates_dict = get_coordinates(treasure['coordinates'])
            coordinates = (coordinates_dict['lat'], coordinates_dict['long'])
            folium.Marker(
                location=coordinates,
                radius=8,
                icon=folium.Icon(color="red"),
                popup='Clue: ' + treasure['clue']
            ).add_to(maps)
    maps = maps._repr_html_()
    return maps


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
