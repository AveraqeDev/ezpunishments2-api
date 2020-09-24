from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
PROFILE_URL = reverse("user:profile")


def create_user(**params):
    """Creates a sample user for tests"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the publicly available user API endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {"username": "smiileyface", "password": "Testpass123"}
        res = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(username=payload["username"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {"username": "smiileyface", "password": "Testpass123"}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {"username": "smiileyface", "password": "pw"}

        res = self.client.post(CREATE_USER_URL, payload)

        user_exists = get_user_model().objects.filter(username=payload["username"])

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {"username": "smiileyface", "password": "Testpass123"}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given"""
        create_user(username="smiileyface", password="Testpass123")
        payload = {"username": "smiileyface", "password": "wrong"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_no_user(self):
        """Test that a token is not created if user doesn't exist"""
        payload = {"username": "smiileyface", "password": "Testpass123"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_missing_field(self):
        """Test that username and password are required to retrieve token"""
        payload = {"username": "smiileyface", "password": ""}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_profile_unauthorized(self):
        """Test that authentication is required for profile endpoint"""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test user API endpoints that require authentication"""

    def setUp(self):
        self.user = create_user(username="smiileyface", password="Testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data, {"username": self.user.username, "mc_uuid": self.user.mc_uuid}
        )

    def test_profile_post_not_allowed(self):
        """Test that POST is not allowed on the profile endpoint"""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {"password": "NewPassword123"}

        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload["password"]))
