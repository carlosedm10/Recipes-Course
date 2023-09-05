"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""

    tags = TagSerializer(
        many=True, required=False
    )  # many=True because it's a list. Also this is a nested serializer.

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]  # We don't want to change the id field.

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags."""
        auth_user = self.context["request"].user  # We get the authenticated user.

        # We are looping through the tags and creating them.
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,  # This equals to name=tag["name"], but we use this for future proofing.
            )
            recipe.tags.add(tag_obj)

    # This method lets us overried the recipe serializer.
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop(
            "tags", []
        )  # We pop the tags, removing them from the validated data.

        recipe = Recipe.objects.create(**validated_data)  # We create the recipe.

        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
