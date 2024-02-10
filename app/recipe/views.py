"""
Views for the recipe app
"""


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer, TagSerializer,
    IngredientSerializer,
    RecipeImageUploadSerializer
)


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

    # Override the get_serializer_class method to return
    # the appropriate serializer class based on the action being performed
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageUploadSerializer
        return self.serializer_class

    # perform_create method runs before the serializer.save() on post requests
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        # Get the recipe object
        recipe = self.get_object()

        # Get the serializer for the recipe and the request data
        serializer = self.get_serializer(recipe, data=request.data)

        # Check if the serializer is valid
        if serializer.is_valid():
            # Save the serializer data and return a success response
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return error response with serializer errors
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewset(viewsets.ModelViewSet):
    """ Manage tags in the database """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Return objects for the current authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new tag """
        serializer.save(user=self.request.user)


class IngredientViewset(viewsets.ModelViewSet):
    """ Manage ingredients in the database """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Return objects for the current authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new ingredient """
        serializer.save(user=self.request.user)
