"""
Tests for recipe APIs
"""
import tempfile
import os

from PIL import Image

from decimal import Decimal  # Used to ensure that the price field is a decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """Helper function to create a recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal(5.00),
        'description': 'Sample description',
        'link': 'https://www.example.com',
    }
    defaults.update(params)  # Update the defaults with the params passed in
    # Create the recipe with the user and the defaults
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the publicly available recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the private recipe API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'pass@123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'test2@123'
        )
        create_recipe(user2)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 10,
            'price': Decimal('4.99'),
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        # serializer = RecipeDetailSerializer(recipe)

        # self.assertEqual(res.data, serializer.data)
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        link = 'https://www.example.com'
        recipe = create_recipe(self.user, title='Old recipe', link=link)

        payload = {'title': 'New recipe'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # Refresh the recipe from the database
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, recipe.link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = create_recipe(self.user)

        payload = {
            'title': 'New recipe',
            'time_minutes': 15,
            'price': Decimal('4.99'),
            'description': 'New description',
            'link': 'https://www.example.com',
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # Refresh the recipe from the database
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_change_user_give_error(self):
        """Test that a user can't change another user's recipe"""
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'test2@123'
        )
        recipe = create_recipe(self.user)

        payload = {'user': user2}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()  # Refresh the recipe from the database
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_user_cannot_delete(self):
        """Test that a user can't delete another user's recipe"""
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'test2@123'
        )
        recipe = create_recipe(user2)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):
        """Test creating a new recipe with tags"""

        recipe_payload = {
            'title': 'Sample recipe',
            'time_minutes': 10,
            'price': Decimal('4.99'),
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
        }
        res = self.client.post(RECIPE_URL, recipe_payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in recipe_payload['tags']:
            exists = recipe.tags.filter(
                user=self.user, name=tag['name']).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a new recipe with existing tags"""
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        # tag2 = Tag.objects.create(user=self.user, name='tag2')
        recipe_payload = {
            'title': 'Sample recipe',
            'time_minutes': 10,
            'price': Decimal('4.99'),
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
        }
        res = self.client.post(RECIPE_URL, recipe_payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        # check all the payload tags exist in the recipe tags
        for tag in recipe_payload['tags']:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag on update of recipe"""
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'tag1'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='tag1')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_ingredient(self):
        """Test creating a recipe with ingredients"""

        recipe_payload = {
            'title': 'Tea',
            'time_minutes': 10,
            'price': Decimal('4.99'),
            'ingredients': [{'name': 'Cinnamon'},
                            {'name': 'Sugar'},
                            {'name': 'Tea Powder'}],
        }
        res = self.client.post(RECIPE_URL, recipe_payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 3)

        for ingredient in recipe_payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user, name=ingredient['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test Create a recipe with existing ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cinnamon')
        recipe_payload = {
            'title': 'Tea',
            'time_minutes': 10,
            'price': Decimal('4.99'),
            'ingredients': [{'name': 'Cinnamon'},
                            {'name': 'Sugar'},
                            {'name': 'Tea Powder'}],
        }
        res = self.client.post(RECIPE_URL, recipe_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 3)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredients in recipe_payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user, name=ingredients['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient on update of recipe"""
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'ing1'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='ing1')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe"""
        ingredient = Ingredient.objects.create(user=self.user, name='ing1')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        ingredient2 = Ingredient.objects.create(user=self.user, name='ing2')
        payload = {'ingredients': [{'name': 'ing2'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test Clear all ingredients from recipe"""
        ingredient = Ingredient.objects.create(user=self.user, name='ing1')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_flter_by_tags(self):
        """Test filtering recipes by tags"""
        recipe1 = create_recipe(user=self.user, title='Recipe1')
        recipe2 = create_recipe(user=self.user, title='Recipe2')
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title='Recipe3')

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPE_URL, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients"""
        recipe1 = create_recipe(user=self.user, title='Recipe1')
        recipe2 = create_recipe(user=self.user, title='Recipe2')
        ing1 = Ingredient.objects.create(user=self.user, name='ing1')
        ing2 = Ingredient.objects.create(user=self.user, name='ing2')

        recipe1.ingredients.add(ing1)
        recipe2.ingredients.add(ing2)
        recipe3 = create_recipe(user=self.user, title='Recipe3')

        params = {'ingredients': f'{ing1.id},{ing2.id}'}
        res = self.client.get(RECIPE_URL, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user4@example.com',
            'test@123'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        """
        This function is used to clean up after each test by
          deleting the image associated with a recipe.
        """
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading a image to the recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
