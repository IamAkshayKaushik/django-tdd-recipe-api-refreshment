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
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id',
                  'title',
                  'time_minutes',
                  'price',
                  'link',
                  'user',
                  'tags',
                  'ingredients',
                  ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a new recipe"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
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

        # Create or get ingredients, and add to the recipe
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view"""

    class Meta(RecipeSerializer.Meta):  # inherit the fields from the parent
        fields = RecipeSerializer.Meta.fields + ['description', 'image']

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()  # delete all the tags
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(
                    user=instance.user,
                    **tag
                )
                instance.tags.add(tag_obj)

        if ingredients is not None:
            # `instance.ingredients.clear()` clears all the ingredients
            # associated with the recipe instance.
            #  It removes all the existing ingredients from the
            # ManyToMany relationship between the Recipe and Ingredient models.
            # This is done before adding the new ingredients provided in the
            # `ingredients` field of the validated data.
            instance.ingredients.clear()  # delete all the ingredients
            for ingredient in ingredients:
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    user=instance.user,
                    **ingredient
                )
                instance.ingredients.add(ingredient_obj)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
        # return super().update(instance, validated_data)


class RecipeImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

    # def save(self, **kwargs):
    #     """Save the image in the recipe object"""
    #     self.recipe.image = self.validated_data['image']
    #     self.recipe.save()
    #     return self.recipe
