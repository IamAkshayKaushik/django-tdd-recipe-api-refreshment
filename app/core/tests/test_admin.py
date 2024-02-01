"""
Test for Django Admin Modifications
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):
    """Tests for Django Admin"""

    def setUp(self):
        """create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = "admin@example.com",
            password = "Admin@123"
        )

        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email = "user@example.com",
            password = "User@123",
            name = "Test User"
        )

    def test_user_list(self):
        """Test that users are listed on page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # retrieve the user edit page
        res = self.client.get(url)

        # check that the response is 200 OK
        self.assertEqual(res.status_code, 200)


    def test_create_user_page(self):
        """Test create user page works"""
        url = reverse('admin:core_user_add')
        # retrieve the create user page
        res = self.client.get(url)

        # check that the response is 200 OK
        self.assertEqual(res.status_code, 200)