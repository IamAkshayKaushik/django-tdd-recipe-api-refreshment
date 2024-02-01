"""
Database models
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """ Custom user model manager where email is the unique identifiers for authentication"""

    def create_user(self, email, password=None, **extra_fields):
        """ Create and save a new user """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create and save a new superuser """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username
        This model defines a custom User class that uses email as the
        username field instead of a separate username field. It inherits
        from AbstractBaseUser to define custom user models and
        PermissionsMixin to support permissions.
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'