"""
Serializers for the user API view.
"""
import email
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


# ModelSerializer is a serializer that converts the JSON data into a python object
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object."""

    class Meta:  # Meta class allows us to configure the ModelSerializer.
        model = get_user_model()
        fields = [
            "email",
            "password",
            "name",
        ]  # Here we should only include the fields that we want to make accessible in the API so the user can change them.
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(
        self, validated_data
    ):  # This will only happen after the data has been validated.
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user and return it"""
        password = validated_data.pop(
            "password", None
        )  # pop() removes the password from the validated data and sets it to None if it doesn't exist.
        user = super().update(
            instance, validated_data
        )  # super() calls the ModelSerializer's update() function.

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token."""

    # Define email and password fields
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    # Custom validation method for user authentication
    def validate(self, attrs):
        """Validate and authenticate the user."""

        # Get email and password from input data
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate the user using email and password
        user = authenticate(
            request=self.context.get("request"),  # Request context for authentication
            username=email,  # Using email as the username
            password=password,
        )

        # Check if authentication was successful
        if not user:
            message = "Unable to authenticate with provided credentials."
            raise serializers.ValidationError(message, code="authentication")

        # If authentication was successful, store the user object in attrs
        attrs["user"] = user
        return attrs
