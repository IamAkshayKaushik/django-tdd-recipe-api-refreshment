"""
Views for the recipe app
"""

from django.utils.translation import gettext as _

from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

class RecipeViewset(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        queryset = self.queryset.filter(user=self.request.user).order_by('-id')
        return queryset

    # Override the get_serializer_class method to return the appropriate serializer class based on the action being performed
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action =='list':
            return RecipeSerializer
        return self.serializer_class

    # perform_create method runs before the serializer.save() on post requests
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)