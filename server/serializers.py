from rest_framework_mongoengine import serializers
from server.models import *


class UserSerializer(serializers.DocumentSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GameSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class ChatSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Chat
        fields = "__all__"