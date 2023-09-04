"""
Tests for the Django admin modifications
"""
from webbrowser import get
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """
    Tests for the Django admin
    """

    def setUp(self):
        """
        Create user and client
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
            name="Test user",
        )

    def test_user_list(self):
        """
        Test that users are listed on user page
        """
        print("Testing user list...")
        url = reverse(
            "admin:core_user_changelist"
        )  # This brings the url where the user list is
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)
        print("User list test: OK")

    def test_edit_user_page(self):
        """
        Test that the edit user page works
        """
        print("Testing edit user page...")
        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, 200
        )  # 200 is the http status code for OK
        print("Edit user page test: OK")

    def test_create_user_page(self):
        """
        Test that the create user page works
        """
        print("Testing create user page...")
        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        print("Create user page test: OK")
