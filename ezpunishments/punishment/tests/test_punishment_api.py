from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from ezpunishments.core.models import Punishment
from ezpunishments.punishment.serializers import PunishmentSerializer

from datetime import datetime
from datetime import timedelta
from django.utils.timezone import make_aware


PUNISHMENT_URL = reverse("punishment:punishment-list")


def detail_url(punishment_id):
    return reverse("punishment:punishment-detail", args=[punishment_id])


def sample_punishment(**params):
    """Create and return a sample punishment"""
    defaults = {
        "mc_username": "SamieMarie",
        "reason": "Being a noob",
        "proof": "https://someproofhere.com/proof",
        "punished_by": "smiileyface",
        "expires": datetime.now() + timedelta(days=7),
    }
    defaults.update(params)

    return Punishment.objects.create(**defaults)


class PublicPunishmentApiTests(TestCase):
    """Test the publically available punishment API endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required"""
        res = self.client.get(PUNISHMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePunishmentApiTests(TestCase):
    """Test punishment API enpoints that require authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="smiileyface", password="Testpass123"
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)

    def test_create_punishment(self):
        """Test creating a punishment"""
        payload = {
            "mc_username": "SamieMarie",
            "reason": "Being a noob",
            "proof": "https://someproofhere.com/proof",
            "punished_by": "smiileyface",
            "expires": make_aware(datetime.now() + timedelta(days=7)),
        }
        res = self.client.post(PUNISHMENT_URL, payload)
        punishment = Punishment.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(punishment, key))

    def test_update_punishment(self):
        """Test updaing a punishment with patch"""
        punishment = sample_punishment()

        payload = {"is_active": False, "removed_by": "smiileyface"}

        self.client.patch(detail_url(punishment.id), payload)

        punishment.refresh_from_db()

        self.assertFalse(punishment.is_active)
        self.assertEqual(punishment.removed_by, payload["removed_by"])

    def test_retrieve_punishments_success(self):
        """Test retrieving punishments is successful"""
        sample_punishment(mc_username="RiseNinja")
        sample_punishment()

        res = self.client.get(PUNISHMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_punishments_by_username(self):
        """Test returning punishments of specified users"""
        punishment1 = sample_punishment()
        punishment2 = sample_punishment(mc_username="Notch")
        punishment3 = sample_punishment(mc_username="RiseNinja")

        res = self.client.get(
            PUNISHMENT_URL,
            {"mc_username": f"{punishment1.mc_username},{punishment2.mc_username}"},
        )

        serializer1 = PunishmentSerializer(punishment1)
        serializer2 = PunishmentSerializer(punishment2)
        serializer3 = PunishmentSerializer(punishment3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_punishments_by_punisher(self):
        """Test returning punishments of specified punishers"""
        punishment1 = sample_punishment()
        punishment2 = sample_punishment(punished_by="Notch")
        punishment3 = sample_punishment(punished_by="RiseNinja")

        res = self.client.get(
            PUNISHMENT_URL,
            {"punished_by": f"{punishment1.punished_by},{punishment2.punished_by}"},
        )

        serializer1 = PunishmentSerializer(punishment1)
        serializer2 = PunishmentSerializer(punishment2)
        serializer3 = PunishmentSerializer(punishment3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
