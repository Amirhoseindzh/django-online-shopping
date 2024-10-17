# app/tests.py
from django.test import TestCase
from .models import User


class UserModelTest(TestCase):

    def test_create_regular_user_is_inactive(self):
        """
        Test that regular users are created with is_active=False.
        """
        user = User.objects.create_user(username='alireza', email='regularuser1@example.com', password='password123')
        self.assertFalse(user.is_active, msg="Regular users should be inactive by default")

    def test_create_superuser_is_active(self):
        """
        Test that superusers are created with is_active=True.
        """
        superuser = User.objects.create_superuser(username='_admin',email='admin1@example.com', password='admin123')
        self.assertTrue(superuser.is_active, msg="Superusers should be active by default")
