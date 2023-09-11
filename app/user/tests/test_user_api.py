"""
Tests for user api
"""

import email
from urllib import response
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import (
    APIClient,
)  # APIClient is a test client that allows us to make requests to our API from our unit tests.
from rest_framework import status

CREATE_USER_URL = reverse(
    "user:create"
)  # reverse() is a helper function that allows us to generate URLs for our Django admin page.
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user with valid payload is successful."""
        payload = {
            "email": "test@example.com",
            "password": "Testpass123",
            "name": "Test Name",
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )  # HTTP 201 response indicates that the object has been created successfully.
        user = get_user_model().objects.get(
            email=payload["email"]
        )  # get() is a helper function that allows us to retrieve objects from the database.
        self.assertTrue(
            user.check_password(payload["password"])
        )  # check_password() is a helper function that allows us to check if the password is correct.
        self.assertNotIn(
            "password", response.data
        )  # This checks that the password is not returned in the response.

    def test_user_with_email_exists_error(self):
        """Test creating a user that already exists."""
        payload = {
            "email": "test@example.com",
            "password": "Testpass123",
            "name": "Test Name",
        }
        create_user(**payload)  # We are creating a user.
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # HTTP 400 response indicates that the request was invalid.

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters."""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name",
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # HTTP 400 response indicates that the request was invalid.
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )  # We are checking that the user was not created.
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            "name": "Test name",
            "email": "test@example.com",
            "password": "Testpass123",
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn(
            "token", response.data
        )  # We are checking that the token is in the response.
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )  # HTTP 200 response indicates that the request was successful.

    def test_create_token_invalid_credentials(self):
        """Test token is not generated if invalid credentials are given"""
        create_user(email="test@example.com", password="goodpass")
        payload = {
            "email": "test@example.com",
            "password": "badpass",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn(
            "token", response.data
        )  # We are checking that the token is not in the response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test token is not generated if password is blank"""
        payload = {
            "email": "test@example.com",
            "password": "",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn(
            "token", response.data
        )  # We are checking that the token is not in the response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users."""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="Testpass123",
            name="Test name",
        )
        self.client = APIClient()
        self.client.force_authenticate(
            user=self.user
        )  # This lets us not use a real authentication.

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        print("Testing retrieve profile...")
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )  # We are checking that the response data is the same as the user data.
        print("Retrieve profile test: OK")

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me endpoint."""
        print("Testing POST not allowed on the me endpoint...")
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        print("POST not allowed on the me endpoint test: OK")

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user."""
        print("Testing update user profile...")
        payload = {"name": "New name", "password": "Newpass123"}
        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # This refreshes the user object with the latest data from the database.
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Update user profile test: OK")
