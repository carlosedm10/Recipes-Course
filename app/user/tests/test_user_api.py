"""
Tests for user api
"""

import email
from urllib import response
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient # APIClient is a test client that allows us to make requests to our API from our unit tests.
from rest_framework import status

CREATE_USER_URL = reverse('user:create') # reverse() is a helper function that allows us to generate URLs for our Django admin page.

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
            'email': 'test@example.com',
            'password': 'Testpass123',
            'name': 'Test Name',
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # HTTP 201 response indicates that the object has been created successfully.
        user = get_user_model().objects.get(email=payload['email']) # get() is a helper function that allows us to retrieve objects from the database.
        self.assertTrue(user.check_password(payload['password'])) # check_password() is a helper function that allows us to check if the password is correct.
        self.assertNotIn('password', response.data) # This checks that the password is not returned in the response.

    def test_user_with_email_exists_error(self):
        """Test creating a user that already exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'Testpass123',
            'name': 'Test Name',
        }
        create_user(**payload) # We are creating a user.
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # HTTP 400 response indicates that the request was invalid.

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # HTTP 400 response indicates that the request was invalid.
        user_exists = get_user_model().objects.filter(email=payload['email']).exists() # We are checking that the user was not created.
        self.assertFalse(user_exists)