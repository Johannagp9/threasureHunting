from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
##TEMPLATES
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from client.services.service import authenticate_user
from client.services.user_service import get_user_by_token, create_user

LOGIN_TEMPLATE = "login.html"
REGISTER_USER_TEMPLATE = "register.html"


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)

@csrf_exempt
def auth_user(request):
    id_token = request.POST.get('token')
    idinfo = authenticate_user(id_token)
    if idinfo is not None:
        return render(request, REGISTER_USER_TEMPLATE)
    else:
        return render(request, LOGIN_TEMPLATE)

def check_response(request, response):
    if isinstance(response, HttpResponse):
        if response.status_code == 401:
            return render(request, LOGIN_TEMPLATE)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def guardar_usuario(request):

    idinfo = request.session.get("token")
    user = {"google_id": idinfo['sub'],
               "name": request.POST.get("name"),
               "email": idinfo['email'],
               "admin": False}
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