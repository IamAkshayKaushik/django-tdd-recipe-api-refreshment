"""
Serializer for the recipe API
"""


from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object"""

    '''This field is used to ensure that the author field
    is a string and not a user object'''
    user = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id',
                  'title',
                  'time_minutes',
                  'price',
                  'link',
                  'user',
                  'tags'
                  ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a new recipe"""
        tags = validated_data.pop('tags', [])
        # Create the recipe with the user and the defaults
        # and the tags passed in
        recipe = Recipe.objects.create(**validated_data)

        auth_user = self.context['request'].user  # get the authenticated user

        # Create or get tags, and add to the recipe
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view"""

    class Meta(RecipeSerializer.Meta):  # inherit the fields from the parent
        fields = RecipeSerializer.Meta.fields + ['description']

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(
                    user=instance.user,
                    **tag
                )
                instance.tags.add(tag_obj)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
        # return super().update(instance, validated_data)
