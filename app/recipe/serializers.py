"""
Serializer for the recipe API
"""


from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object"""

    '''This field is used to ensure that the author field
    is a string and not a user object'''
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'user']
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view"""

    class Meta(RecipeSerializer.Meta):  # inherit the fields from the parent
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
