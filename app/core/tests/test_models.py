"""Test form models"""
from random import sample

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="user@example.com", password="Testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        print("Testing create user with email...")
        email = "test@example.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(
            user.check_password(password)
        )  # we use check_password() due to the password is encrypted.
        print("Create user with email test: OK")

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        print("Testing normalizing email...")
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="Testpass123"
            )
            self.assertEqual(user.email, expected)
        print("Normalized email test: OK")

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises error."""
        print("Testing create user without email raises error...")
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password="Testpass123")
        print("Create user without email raises error test: OK")

    def test_create_superuser(self):
        """Test creating a new superuser."""
        print("Testing create superuser...")
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "Testpass123",
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        print("Create superuser test: OK")

    def test_create_recipe(self):
        """Test creating a new recipe is successful."""
        print("Testing create recipe...")
        user = get_user_model().objects.create_user("test@example.com", "Testpass123")
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("10.50"),  # we use Decimal() to avoid floating point error.
            description="Sample recipe description",
        )
        self.assertEqual(str(recipe), recipe.title)
        print("Create recipe test: OK")

    def test_create_tag(self):
        """Test creating a new tag is successful."""
        print("Testing create tag...")
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="tag1")

        self.assertEqual(str(tag), tag.name)
        print("Create tag test: OK")

    def test_create_ingredient(self):
        """Test creating a new ingredient is successful."""

        print("Testing create ingredient...")
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name="ingredient1")

        self.assertEqual(str(ingredient), ingredient.name)  # __str__ method
        print("Create ingrediente test: OK")
