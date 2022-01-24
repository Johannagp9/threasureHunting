import django_mongoengine_filter
from .models import *

class GameFilter(django_mongoengine_filter.FilterSet):
    class Meta:
        model = Game
        fields = []