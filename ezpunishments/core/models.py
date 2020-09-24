from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

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
