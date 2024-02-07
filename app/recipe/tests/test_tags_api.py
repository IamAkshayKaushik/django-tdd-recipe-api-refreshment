"""
Tests for the tags API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Return the detail URL for the tag"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(**params):
    """Helper function to create a new user"""

    default_user = {
        'email': 'user@example.com',
        'password': 'user@1234',
        'name': 'Test User'
    }
    default_user.update(params)  # Update the default_user with the params
    return get_user_model().objects.create_user(**default_user)


class PublicTagsApiTests(TestCase):
    """Test the unauthenticated API requests"""

    def setUP(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Veg')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        '''because different database backends return different order'''
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = create_user(email='user2@example.com', password='user2@1234')
        Tag.objects.create(user=user2, name='Keto')
        tag = Tag.objects.create(user=self.user, name='Gluten-free')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag_name(self):
        """Test updating a tag name"""
        tag = Tag.objects.create(user=self.user, name='Veg')

        payload = {'name': 'Vegan'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Veg')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # used filter bcoz get throw error if no tag found
        tag = Tag.objects.filter(user=self.user)
        self.assertFalse(tag.exists())
