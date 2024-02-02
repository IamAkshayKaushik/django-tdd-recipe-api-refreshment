"""
Serializers for the user api
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True,'min_length': 5}} # This is a security measure to ensure that passwords are not sent over the network

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)