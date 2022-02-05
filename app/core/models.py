from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username="", **extra_fields):
        """Creates and save a new user"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user mode"""

    email = models.EmailField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField(related_name="user_creator", editable=False)
    updated_by = CurrentUserField(on_update=True, related_name="user_update")

    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class ProductModel(models.Model):
    """Product Admin"""

    code = models.CharField(max_length=30, blank=False, null=False)
    name = models.CharField(max_length=50, blank=False, null=False)
    product_type = models.CharField(max_length=50, blank=False, null=False)
    availability = models.BooleanField(blank=False, null=False)
    needing_repair = models.BooleanField(blank=False, null=False)
    durability = models.PositiveIntegerField(default=0)
    max_durability = models.PositiveIntegerField(blank=False, null=False)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=False, null=False)
    minimum_rent_period = models.PositiveSmallIntegerField(blank=False, null=False)
    created_by = CurrentUserField(related_name="school_admin_creator", editable=False)
    updated_by = CurrentUserField(on_update=True, related_name="school_admin_update")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
