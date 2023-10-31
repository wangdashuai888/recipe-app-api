"""
tests for the user api
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
    create a user helper function
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    test the users api (public)
    """

    def setUp(self):
        """
        setup function
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        test creating user with valid payload is successful
        """
        payload = {
            'email': 'user@test.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check if user was created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        # check if password is not returned in response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        """
        test creating user that already exists fails
        """
        payload = {
            'email': 'user@test.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_short_password(self):
        """
        test that password must be more than 5 characters
        """
        payload = {
            'email': 'user2@test.com',
            'password': 'pw123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # check if user was created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        test that a token is created for the user
        """
        user_details = {
            'email': 'test@test.com',
            'name': 'Test Name',
            'password': 'testpass123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        test that token is not created if invalid credentials are given
        """
        user_details = {
            'email': 'test@test.com',
            'name': 'Test Name',
            'password': 'testpass123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': 'wrongpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_pass(self):
        """
        test that token is not created if password is not given
        """
        payload = {
            'email': 'test@test.com',
            'password': ''
            }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """
        test that authentication is required for users
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    test api requests that require authentication
    """

    def setUp(self):
        """
        setup function
        """
        self.user = create_user(
            email='test@test.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        test retrieving profile for logged in user
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check if response data matches user data
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """
        test that post is not allowed on the me url
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        test updating the user profile for authenticated user
        """
        payload = {
            'name': 'New Name',
            'password': 'newtestpass123',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        # check if user name is updated
        self.assertEqual(self.user.name, payload['name'])
        # check if password is updated
        self.assertTrue(self.user.check_password(payload['password']))
        # check if response status code is 200
        self.assertEqual(res.status_code, status.HTTP_200_OK)
