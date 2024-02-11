"""
Tests for the ingredients API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_LIST = reverse('recipe:ingredient-list')


def create_user(**params):
    """Helper function to create a new user"""

    default_user = {
        'email': 'user@example.com',
        'password': 'user@1234',
        'name': 'Test User'
    }
    default_user.update(params)  # Update the default_user with the params
    return get_user_model().objects.create_user(**default_user)


def detail_url(ingredient_id):
    """Return ingredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test the unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_LIST)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_ingredients_list(self):
        """Test retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name='Veg')
        Ingredient.objects.create(user=self.user, name='Keto')

        res = self.client.get(INGREDIENTS_LIST)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user"""
        user2 = create_user(email='user2@example.com', password='user2@1234')
        Ingredient.objects.create(user=user2, name='Veg')
        ingredient = Ingredient.objects.create(user=self.user, name='Keto')

        res = self.client.get(INGREDIENTS_LIST)
        serializer = IngredientSerializer(ingredient)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        for key, value in serializer.data.items():
            self.assertEqual(value, res.data[0][key])

    def test_update_ingredient_name(self):
        """Test updating an ingredient name"""
        ingredient = Ingredient.objects.create(user=self.user, name='Veg')

        payload = {'name': 'Vegan'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingre = Ingredient.objects.create(user=self.user, name='Veg')

        url = detail_url(ingre.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # used filter bcoz get throw error if no ingredient found
        ingredient = Ingredient.objects.filter(user=self.user).first()
        self.assertIsNone(ingredient)

    def test_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='ing1')
        in2 = Ingredient.objects.create(user=self.user, name='ing2')
        recipe = Recipe.objects.create(
            title='recipe1', time_minutes=5, price=5.00, user=self.user
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_LIST, {'assigned_only': 1})

        serializer1 = IngredientSerializer(in1)
        serializer2 = IngredientSerializer(in2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        ing1 = Ingredient.objects.create(user=self.user, name='ing1')
        Ingredient.objects.create(user=self.user, name='ing2')
        recipe1 = Recipe.objects.create(
            title='recipe1', time_minutes=5, price=5.00, user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='recipe2', time_minutes=5, price=5.00, user=self.user
        )
        recipe1.ingredients.add(ing1)
        recipe2.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_LIST, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
