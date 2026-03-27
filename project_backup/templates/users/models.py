"""Custom user model for ECP authentication."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with email login and ECP public key.

    Extends AbstractUser — inherits username, email, password,
    is_staff, is_active, date_joined and all standard fields.
    Adds email as unique identifier and public_key for ECP auth.
    Private key is NEVER stored — only returned to user at registration.

    Example:
        user = User.objects.get(email='user@example.com')
        print(user.public_key)
    """

    email = models.EmailField(
        unique=True,
        verbose_name='Email address',
        help_text='Required. Used as the primary login identifier.',
    )
    public_key = models.TextField(
        blank=True,
        default='',
        verbose_name='ECP public key',
        help_text='PEM-encoded EC public key. Private key is never stored.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self) -> str:
        """Return email as string representation.

        Returns:
            User email address.
        """
        return self.email