"""
Tests for the ingredients API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Return ingredient detail URL."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="Testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthorized ingredients API access."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to call API."""

        print("Test that login is required to call API.")
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print("Test that login is required to call API: OK")


class PrivateIngredientsApiTests(TestCase):
    """Test authorized ingredients API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients."""

        print("Test retrieving ingredients.")
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        response = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        print("Test retrieving ingredients: OK")

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned."""

        print("Test that ingredients for the authenticated user are returned.")
        user2 = create_user(
            email="user2@example.com", password="testpass123"
        )  # this user isn't authenticated
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(
            user=self.user, name="Tumeric"
        )  # this user is authenticated.

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)
        self.assertEqual(response.data[0]["id"], ingredient.id)

        print("Test that ingredients for the authenticated user are returned: OK")

    def test_update_ingredient(self):
        """Test updating an ingredient"""

        print("Test updating an ingredient.")
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar")
        payload = {"name": "Salt"}
        url = detail_url(ingredient.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

        print("Test updating an ingredient: OK")

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""

        print("Test deleting an ingredient.")
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar")
        url = detail_url(ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

        print("Test deleting an ingredient: OK")

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test listing ingredients by those assigned to recipes"""

        print("Testing listing ingredients by those assigned to recipes.")
        ingredient1 = Ingredient.objects.create(user=self.user, name="Apples")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Turkey")

        recipe = Recipe.objects.create(
            title="Apple crumble",
            time_minutes=5,
            price=Decimal("10.00"),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

        print("Test listing ingredients by those assigned to recipes: OK")

    def test_filtered_ingredients_unique(self):
        """Test filtering ingredients by assigned returns unique items"""

        print("Test filtering ingredients by assigned returns unique items.")
        ingredient = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Cheese")

        recipe1 = Recipe.objects.create(
            title="Eggs benedict",
            time_minutes=30,
            price=Decimal("12.00"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_minutes=20,
            price=Decimal("5.00"),
            user=self.user,
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        response = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)

        print("Test filtering ingredients by assigned returns unique items: OK")
