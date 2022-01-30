import django_mongoengine_filter
from .models import *


class UserFilter(django_mongoengine_filter.FilterSet):
    name = django_mongoengine_filter.filters.StringFilter(lookup_type='icontains')

    class Meta:
        model = User
        fields = ['email', 'birth_date', 'google_id']

class GameFilter(django_mongoengine_filter.FilterSet):
    class Meta:
        model = Game
        fields = []

class ChatFilter(django_mongoengine_filter.FilterSet):
    class Meta:
        model = Chat
        fields = ['sender', 'receiver']