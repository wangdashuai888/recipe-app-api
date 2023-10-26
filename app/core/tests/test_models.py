"""
test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """test models"""

    def test_create_user_with_email_successful(self):
        """test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test the email for a new user is normalized"""
        emails = [
            ['test1@TEST.com','test1@test.com'],  # noqa
            ['Test2@Test.com','Test2@test.com'],  # noqa
            ['TEST3@TEST.COM','TEST3@test.com'],  # noqa
        ]
        for email, expected in emails:
            user = get_user_model().objects.create_user(
                email,
                password='testpass123'
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):
        """test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """test creating super user"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
