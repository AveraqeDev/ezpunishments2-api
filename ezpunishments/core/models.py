from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.timezone import make_aware

import requests


def get_mc_uuid(username):
    """Gets the Minecraft UUID for a username"""
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    res = requests.get(url)
    if res.status_code == 204:
        raise ValueError("Users must have a valid MC username")
    else:
        return res.json().get("id")


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not username:
            raise ValueError("Users must have a valid MC username")
        mc_uuid = get_mc_uuid(username)
        user = self.model(username=username, mc_uuid=mc_uuid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        """Creates and saves a new superuser"""
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports mc_uuid"""

    username = models.CharField(max_length=16, unique=True)
    mc_uuid = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"


class PunishmentManager(models.Manager):
    def create(self, mc_username, reason, punished_by, expires, **extra_fields):
        """Creates and saves a new Punishment"""
        if not mc_username or not reason or not punished_by or not expires:
            raise ValueError(
                "Punishments must have user, reason, punished by and expires fields"
            )
        mc_uuid = get_mc_uuid(mc_username)
        punished_by_uuid = get_mc_uuid(punished_by)
        if not expires.tzinfo:
            expires = make_aware(expires)
        punishment = self.model(
            mc_username=mc_username,
            mc_uuid=mc_uuid,
            reason=reason,
            punished_by=punished_by,
            punished_by_uuid=punished_by_uuid,
            expires=expires,
            **extra_fields,
        )
        punishment.save(using=self._db)

        return punishment


class Punishment(models.Model):
    """Punishment object"""

    mc_username = models.CharField(max_length=16)
    mc_uuid = models.CharField(max_length=255)
    reason = models.CharField(max_length=255)
    proof = models.CharField(max_length=255, null=True)
    punished_by = models.CharField(max_length=16)
    punished_by_uuid = models.CharField(max_length=255)
    removed_by = models.CharField(max_length=16, null=True, default=None)
    removed_by_uuid = models.CharField(max_length=255, null=True, default=None)
    is_active = models.BooleanField(default=True)
    expires = models.DateTimeField()
    date_punished = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    objects = PunishmentManager()
