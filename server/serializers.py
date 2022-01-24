from rest_framework_mongoengine import serializers
from server.models import User


class UserSerializer(serializers.DocumentSerializer):
    class Meta:
        model = User
        fields = '__all__'
