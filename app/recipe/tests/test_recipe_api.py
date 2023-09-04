"""
Tests for recipe APIs
"""
from decimal import Decimal
from urllib import response

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """Helper function to create a new recipe."""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 10,
        "price": Decimal("5.20"),
        "description": "Sample description",
    }
    defaults.update(
        params
    )  # update the defaults with the params passed in the function.

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the public (unauthenticated) recipe APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that login is required to call API."""
        print("Test that login is required to call API.")
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print("Test that login is required to call API: OK")


class PrivateRecipeApiTests(TestCase):
    """Test the private (authenticated) recipe APIs."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        print("Testing retrieving recipes...")
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        print("Test retrieving recipes: OK")

    def test_recipes_limited_to_user(self):
        """Test that recipes is limited to authenticated user."""
        print("Testing that recipes is limited to authenticated user...")
        user2 = get_user_model().objects.create_user("user2@example.com", "password123")
        create_recipe(user=user2)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 1
        )  # only one recipe for the authenticated user
        self.assertEqual(response.data, serializer.data)  # the recipe is the same

        print("Test that recipes is limited to authenticated user: OK")

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        print("Testing get recipe detail...")

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)

        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

        print("Test get recipe detail: OK")

    def test_create_recipe(self):
        """Test creating recipe."""
        print("Testing creating recipe...")

        payload = {
            "title": "Chocolate cheesecake",
            "time_minutes": 30,
            "price": Decimal("5.00"),
        }

        response = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=response.data["id"])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        self.assertEqual(recipe.user, self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print("Test creating recipe: OK")
