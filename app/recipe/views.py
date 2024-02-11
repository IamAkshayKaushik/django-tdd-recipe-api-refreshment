"""
Views for the recipe app
"""
from drf_spectacular.utils import (extend_schema,
                                   extend_schema_view,
                                   OpenApiTypes,
                                   OpenApiParameter)


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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewset(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _parameters_to_ints(self, query_string):
        """Split query_string by comma and convert each string ID to integer"""
        # query_string = '1,2,3'
        return [int(str_id) for str_id in query_string.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        tags = self.request.query_params.get('tags', None)
        ingredients = self.request.query_params.get('ingredients', None)
        queryset = self.queryset

        if tags:
            tag_ids = self._parameters_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._parameters_to_ints(ingredients)
            queryset = queryset.filter(
                ingredients__id__in=ingredient_ids
            )
        queryset = queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,
                enum=[0, 1],
                description='Filter by items assigned to recipes',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(viewsets.ModelViewSet):
    """ Base viewset for recipe attributes
        I use this for both ingredients and tags
        to avoid duplicating code
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Return objects for the current authenticated user only """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """ Create a new ingredient """
        serializer.save(user=self.request.user)


class TagViewset(BaseRecipeAttrViewSet):
    """ Manage tags in the database """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewset(BaseRecipeAttrViewSet):
    """ Manage ingredients in the database """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
