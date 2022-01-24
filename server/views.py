from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework_mongoengine import generics
from serializers import *
from filters import *

# Create your models here.
decorators = [never_cache]

@method_decorator(decorators, name='dispatch')
class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get(self, request, *args, **kwargs):
        token = request.headers['Authorization']
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

    def filter_queryset(self, queryset):
        filter_game= GameFilter(self.request.query_params, queryset=queryset)
        return filter_game.qs


@method_decorator(decorators, name='dispatch')
class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

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

