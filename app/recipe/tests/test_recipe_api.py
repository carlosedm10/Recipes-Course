"""
Tests for recipe APIs
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def create_recipe(user, **params):
    """Helper function to create a new recipe."""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 10,
        "price": Decimal("5.20"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }
    defaults.update(
        params
    )  # update the defaults with the params passed in the function.

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email="user3@example.com", password="password123")
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
        user2 = create_user(email="user2@example.com", password="password123")
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
        print(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

        print("Test creating recipe: OK")

    def test_partial_update(self):
        """Test updating a recipe with patch."""
        original_link = "http://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user, link=original_link, title="Original title"
        )
        payload = {
            "title": "New title",
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["link"], original_link)

    def test_full_update(self):
        """Test full update of recipe"""
        print("Testing full update of recipe...")
        recipe = create_recipe(
            user=self.user,
            title="Sample title",
            link="http://example.com/new-recipe.pdf",
            description="Sample description",
        )
        payload = {
            "title": "New title",
            "link": "http://example.com/new-recipe-changed.pdf",
            "description": "New description",
            "time_minutes": 25,
            "price": Decimal("10.00"),
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()  # refresh the recipe from the database.
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test that changing recipe user returns error"""

        print("Testing updating user returns error...")

        new_user = create_user(email="user2@example.com", password="password123")
        recipe = create_recipe(user=self.user)
        payload = {
            "user": new_user,
        }
        url = detail_url(recipe.id)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)  # the user is still the same.
        print("Test updating user returns error: OK")

    def test_delete_recipe(self):
        """Test deleting a recipe."""

        print("Testing deleting a recipe...")

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

        print("Test deleting a recipe: OK")

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete anothers user recipe returns error."""
        print("Testing trying to delete anothers user recipe returns error...")
        new_user = create_user(email="user2@example.com", password="password123")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)
        # This won't work because the user is not the owner of the recipe.

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

        print("Test trying to delete anothers user recipe returns error: OK")

    # ----------------------------------------TAGS----------------------------------------

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        print("Testing creating a recipe with new tags...")

        payload = {
            "title": "Thai Prawn Curry",
            "time_minutes": 30,
            "price": Decimal("5.00"),
            "tags": [{"name": "Thai"}, {"name": "dinner"}],
        }

        response = self.client.post(
            RECIPES_URL, payload, format="json"
        )  # We need to specify the format as json.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)

        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

        print("Test creating a recipe with new tags: OK")

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Chicken Tikka",
            "time_minutes": 30,
            "price": Decimal("5.00"),
            "tags": [{"name": tag_indian.name}, {"name": "dinner"}],
        }

        response = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(
            tag_indian, recipe.tags.all()
        )  # check if the tag is in the recipe tags.

        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

        print("Test creating a recipe with existing tags: OK")

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe"""

        print("Testing creating a tag when updating a recipe...")
        recipe = create_recipe(user=self.user)
        payload = {"tags": [{"name": "Lunch"}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Checking if the new tag is in the recipe tags.
        new_tag = Tag.objects.get(name="Lunch", user=self.user)
        self.assertIn(new_tag, recipe.tags.all())

        print("Test creating a tag when updating a recipe: OK")

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag whe updating a recipe"""

        print("Testing assigning an existing tag whe updating a recipe...")
        tag_breakfast = Tag.objects.create(
            user=self.user, name="Breakfast"
        )  # We create the tag.
        recipe = create_recipe(user=self.user)  # We create the recipe.
        recipe.tags.add(tag_breakfast)  # We add the tag to the recipe.

        tag_lunch = Tag.objects.create(
            user=self.user, name="Lunch"
        )  # We create another tag.
        payload = {
            "tags": [{"name": tag_lunch.name}]
        }  # We create the payload to change the breakfast tag to lunch.
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")  # We patch the recipe.

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

        print("Test assigning an existing tag whe updating a recipe: OK")

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags"""

        print("Testing clearing a recipes tags...")
        tag = Tag.objects.create(user=self.user, name="Dessert")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {"tags": []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

        print("Test clearing a recipes tags: OK")

    # ----------------------------------------INGREDIENTS----------------------------------------

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        print("Testing creating a recipe with new ingredients...")

        payload = {
            "title": "Thai Prawn Curry",
            "time_minutes": 30,
            "price": Decimal("5.00"),
            "ingredients": [{"name": "Prawns"}, {"name": "Curry"}],
        }

        response = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

        print("Test creating a recipe with new ingredients: OK")

    def test_create_reciper_with_existing_ingredient(self):
        """Test creating a recipe with existing ingredients."""
        print("Testing creating a recipe with existing ingredients...")

        ingredient = Ingredient.objects.create(user=self.user, name="Prawns")
        payload = {
            "title": "Thai Prawn Curry",
            "time_minutes": 25,
            "price": Decimal("5.01"),
            "ingredients": [{"name": "coconut milk"}, {"name": "Curry"}],
        }

        response = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

        print("Test creating a recipe with existing ingredients: OK")

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe"""

        print("Testing creating an ingredient when updating a recipe...")
        recipe = create_recipe(user=self.user)

        payload = {"ingredients": [{"name": "Limes"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(name="Limes", user=self.user)
        self.assertIn(new_ingredient, recipe.ingredients.all())

        print("Test creating an ingredient when updating a recipe: OK")

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe"""

        print("Testing assigning an existing ingredient when updating a recipe...")
        ingredient1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name="Chili")
        payload = {"ingredients": [{"name": "Chili"}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

        print("Test assigning an existing ingredient when updating a recipe: OK")

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients"""

        print("Testing clearing a recipes ingredients...")
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

        print("Test clearing a recipes ingredients: OK")

    # ----------------------------------------FILTERS----------------------------------------

    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        print("Testing returning recipes with specific tags...")

        recipe1 = create_recipe(user=self.user, title="Thai curry")
        recipe2 = create_recipe(user=self.user, title="Curry")

        tag1 = Tag.objects.create(user=self.user, name="Thai")
        tag2 = Tag.objects.create(user=self.user, name="Indian")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title="Fish and Chips")

        params = {"tags": f"{tag1.id},{tag2.id}"}
        response = self.client.get(RECIPES_URL, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

        print("Test returning recipes with specific tags: OK")

    def test_filter_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        print("Testing returning recipes with specific ingredients...")

        recipe1 = create_recipe(user=self.user, title="Thai curry")
        recipe2 = create_recipe(user=self.user, title="Curry")

        ingredient1 = Ingredient.objects.create(user=self.user, name="Prawns")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Chicken")

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe(user=self.user, title="Fish and Chips")

        params = {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        response = self.client.get(RECIPES_URL, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

        print("Test returning recipes with specific ingredients: OK")


# ----------------------------------------IMAGE----------------------------------------


class ImageUploadTests(TestCase):
    """Test uploading images."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@example.com", "password")
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(
        self,
    ):  # this method is called after each test, to not build images everytimes.
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""

        print("Testing uploading an image to recipe...")
        url = image_upload_url(self.recipe.id)

        # NOTE: This will create a temporary file that will be deleted after the test.

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))  # create a new image.
            img.save(image_file, format="JPEG")  # save the image to the image file.
            image_file.seek(0)  # move the pointer to the beginning, for uploading it.

            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        print("Testing uploading an invalid image...")
        url = image_upload_url(self.recipe.id)
        payload = {"image": "notimage"}

        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        print("Test uploading an invalid image: OK")
