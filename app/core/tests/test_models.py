"""
Tests for models
"""
from decimal import Decimal # This is used to ensure that the price field is a decimal

from django.test import TestCase
from django.contrib.auth import get_user_model  # get_user_model() returns the User model

from core import models


class ModelTests(TestCase):
    """Test the models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, normalized_email in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, normalized_email)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test Creating a new superuser"""
        user = get_user_model().objects.create_superuser('test@example.com', 'test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_create_recipe(self):
        """Test creating a recipe"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test@123',
            name='Test User'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Test Recipe',
            price=Decimal('4.99'),
            time_minutes = 10,
            description='Recipe Description'
        )
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.price, Decimal('4.99'))
        self.assertEqual(recipe.time_minutes, 10)
        self.assertEqual(recipe.description, 'Recipe Description')