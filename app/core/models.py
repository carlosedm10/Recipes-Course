"""
Database models
"""
import uuid
import os

from django.conf import settings
from collections import UserDict
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]  # get the extension of the file.
    filename = f"{uuid.uuid4()}{ext}"  # generate a random filename.

    return os.path.join("uploads/recipe/", filename)  # return the path.


# NOTE: Using os module to join the path is better than using string concatenation because it will work on any operating system.


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(
            email=self.normalize_email(email), **extra_fields
        )  # create a new user model.
        user.set_password(password)  # this will encrypt the password.
        user.save(using=self._db)  # to support multiple databases just in case.

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # whether the user is active or not.
    is_staff = models.BooleanField(default=False)  # whether the user is staff or not.

    objects = UserManager()  # the object manager for this model.

    USERNAME_FIELD = "email"  # the field that is used to log in.


class Recipe(models.Model):
    """Recipe Object."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # the user that owns the recipe.
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    time_minutes = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(
        max_length=255, blank=True, null=True
    )  # the link to the recipe (optional).
    tags = models.ManyToManyField(
        "Tag"
    )  # the tag(s) that are associated with the recipe.
    ingredients = models.ManyToManyField(
        "Ingredient"
    )  # the ingredient(s) that are associated with the recipe.

    image = models.ImageField(
        null=True, upload_to=recipe_image_file_path
    )  # We are specifying the path where the image will be uploaded.

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag to be used for a filtering recipes."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # the user that owns the tag.

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # the user that owns the ingredient.

    def __str__(self):
        return self.name
