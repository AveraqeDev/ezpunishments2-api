from django.test import TestCase
from django.contrib.auth import get_user_model

from ezpunishments.core import models

from datetime import datetime
from datetime import timedelta


class ModelTests(TestCase):
    def test_create_user_with_username_successful(self):
        """Test creating a new user with username is successful"""
        username = "smiileyface"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            username=username, password=password
        )

        self.assertEqual(user.username, username)
        self.assertEqual(user.mc_uuid, "c6edbd5a24aa440d918a1e299b22e5f9")
        self.assertTrue(user.check_password(password))

    def test_create_user_with_no_username(self):
        """Test creating a new user with no username raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "Testpass123")

    def test_create_user_with_invalid_username(self):
        """Test creating a new user with invalid username raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(">invalid<", "Testpass123")

    def test_create_new_superuser(self):
        """Test creating a new superuser is successful"""
        user = get_user_model().objects.create_superuser(
            username="smiileyface", password="Testpass123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_new_punishment_successful(self):
        """Test creating a new punishment is successful"""
        mc_username = "SamieMarie"
        reason = "Hacking like a noob"
        proof = "https://youtube.com/someproofhere"
        punished_by = "smiileyface"
        expires = datetime.now() + timedelta(days=1)
        punishment = models.Punishment.objects.create(
            mc_username=mc_username,
            reason=reason,
            proof=proof,
            punished_by=punished_by,
            expires=expires,
        )

        self.assertEqual(punishment.mc_username, mc_username)
        self.assertEqual(punishment.mc_uuid, "c5cb9e1c4cbe4563bc55754d59b55a1e"),
        self.assertEqual(punishment.reason, reason),
        self.assertEqual(punishment.proof, proof),
        self.assertEqual(punishment.punished_by, punished_by),
        self.assertEqual(
            punishment.punished_by_uuid, "c6edbd5a24aa440d918a1e299b22e5f9"
        ),
        self.assertTrue(punishment.active)
        self.assertEqual(punishment.expires, expires)

    def test_create_new_punishment_missing_field(self):
        """Test creating a new punishment missing a required field fails"""
        with self.assertRaises(ValueError):
            models.PermissionsMixin.objects.create(punished_by="smiileyface")

    def test_create_new_punishment_invalid_username(self):
        """Test creating a new punishment with invalid MC username fails"""
        with self.assertRaises(ValueError):
            mc_username = ">invalid<"
            reason = "Hacking like a noob"
            proof = "https://youtube.com/someproofhere"
            punished_by = "smiileyface"
            expires = datetime.now() + timedelta(days=1)
            models.Punishment.objects.create(
                mc_username=mc_username,
                reason=reason,
                proof=proof,
                punished_by=punished_by,
                expires=expires,
            )
