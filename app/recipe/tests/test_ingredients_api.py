"""
Tests for the ingredients API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

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
