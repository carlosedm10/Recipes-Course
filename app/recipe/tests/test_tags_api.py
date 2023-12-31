"""
Tests for the tags API.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def tag_detail_url(tag_id):
    """Return tag detail URL."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="Testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthorized tags API access."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to call API."""

        print("Test that login is required to call API.")
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print("Test that login is required to call API: OK")


class PrivateTagsApiTests(TestCase):
    """Test authorized tags API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""

        print("Test retrieving tags.")
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        print("Test retrieving tags: OK")

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user."""

        print("Test that tags returned are for the authenticated user.")
        user2 = create_user(email="user2@example.com", password="Testpass123")
        Tag.objects.create(
            user=user2, name="Fruity"
        )  # We don't assign it to a vairable, just need to created in the db
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)
        self.assertEqual(response.data[0]["id"], tag.id)

        print("Test that tags returned are for the authenticated user: OK")

    def test_update_tag(self):
        """Test updating a tag."""

        print("Test updating a tag.")
        tag = Tag.objects.create(user=self.user, name="Test Tag")
        payload = {"name": "New Tag Name"}
        url = tag_detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

        print("Test updating a tag: OK")

    def test_delete_tag(self):
        """Test deleting a tag."""

        print("Test deleting a tag.")
        tag = Tag.objects.create(user=self.user, name="Test Tag")
        url = tag_detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

        print("Test deleting a tag: OK")

    def test_filter_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes."""

        print("Test filtering tags by those assigned to recipes.")
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        recipe = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_minutes=10,
            price=Decimal("5.00"),
            user=self.user,
        )
        recipe.tags.add(tag1)

        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

        print("Test filtering tags by those assigned to recipes: OK")

    def test_filtered_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items."""

        print("Test filtering tags by assigned returns unique items.")
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Pancakes", time_minutes=5, price=Decimal("3.00"), user=self.user
        )
        recipe2 = Recipe.objects.create(
            title="Porridge", time_minutes=3, price=Decimal("2.00"), user=self.user
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)

        print("Test filtered tags by assigned returns unique items: OK")
