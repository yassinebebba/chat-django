from .models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.save()
        return user
