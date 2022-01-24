import json
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import Http404
from rest_framework_mongoengine import generics
from threasureHunting.settings import GOOGLE_CLIENT_ID
from .serializers import *
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

decorators = [never_cache]


@csrf_exempt
def auth_user(request):
    token = request.POST.get('token')
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # userid = idinfo['sub']
        cache.set(idinfo['sub'], idinfo['sub'], idinfo['exp'])
    except ValueError:
        # Invalid token
        raise Http404("Invalid token")
    return HttpResponse(json.dumps(idinfo), content_type='application/json')


@method_decorator(decorators, name='dispatch')
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        token = request.headers['Authorization']
        print("TOKEN SERVER " + token)
        result = cache.get(token)
        if result is None:
            return HttpResponse('Unauthorized', status=401)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = request.headers['Authorization']
        result = cache.get(token)
        if result is None:
            return HttpResponse('Unauthorized', status=401)
        return self.create(request, *args, **kwargs)


@method_decorator(decorators, name='dispatch')
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get(self, request, *args, **kwargs):
        token = request.headers['Authorization']
        result = cache.get(token)
        if result is None:
            return HttpResponse('Unauthorized', status=401)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        token = request.headers['Authorization']
        result = cache.get(token)
        if result is None:
            return HttpResponse('Unauthorized', status=401)
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        token = request.headers['Authorization']
        result = cache.get(token)
        if result is None:
            return HttpResponse('Unauthorized', status=401)
        return self.destroy(request, *args, **kwargs)