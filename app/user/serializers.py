"""
Serializers for the user API view.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer): # ModelSerializer is a serializer that converts the JSON data into a python object
    """Serializer for the users object."""

    class Meta: # Meta class allows us to configure the ModelSerializer.
        model = get_user_model()
        fields = ('email', 'password', 'name') # Here we should only include the fields that we want to make accessible in the API so the user can change them.
        extra_kwargs = { 'password': { 'write_only': True, 'min_length': 5 } }

    def create(self, validated_data): # This will only happen after the data has been validated.
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)