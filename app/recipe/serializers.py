"""
Serializer for the recipe API
"""

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object"""
    user = serializers.StringRelatedField(read_only=True) # This field is used to ensure that the author field is a string and not a user object

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'user']
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view"""

    class Meta(RecipeSerializer.Meta): # This is used to inherit the fields from the parent class
        fields = RecipeSerializer.Meta.fields + ['description']
