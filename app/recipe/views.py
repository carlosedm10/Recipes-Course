"""
Views for recipe APIs
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""

    serializer_class = (
        serializers.RecipeDetailSerializer
    )  # We use the detailed and then we override the get_serializer_class method.
    queryset = (
        Recipe.objects.all()
    )  # Represents the models that are available in the viewset.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    # this method is used to determine which serializer class to use for the request.
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == "list":
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
