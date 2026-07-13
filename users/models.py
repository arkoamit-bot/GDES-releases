"""
User profile and invitation models for multi-user BGDDR deployment.

Extends Django's built-in User with registry-specific fields (role, department,
phone). Uses a one-to-one UserProfile so we don't replace the auth User model.

Invitation flow:
1. Admin creates an Invitation (email + role).
2. System emails a link with a token (or prints it for hand-delivery in clinics
   without reliable email).
3. User clicks link, sets password, account is created and role assigned.
"""
from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    """One-to-one extension of Django's User for registry-specific fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=30, blank=True,
        choices=[
            ("", "— no role —"),
            ("data_manager", "Data Manager"),
            ("statistician", "Statistician"),
            ("readonly", "Read-only"),
            ("coordinator", "Coordinator"),
            ("investigator", "Investigator"),
            ("pathologist", "Pathologist"),
        ],
        help_text="Determines permissions (seeded by seed_roles).")
    department = models.CharField(max_length=80, blank=True,
                                  help_text="e.g. Dept. of Nephrology")
    phone = models.CharField(max_length=30, blank=True)
    is_clinician = models.BooleanField(
        default=False,
        help_text="Can write prescriptions and sign off on pathology reviews.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role or 'no role'})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep the user's Group membership in sync with the role
        if self.role:
            group, _ = Group.objects.get_or_create(name=self.role)
            self.user.groups.set([group])
        else:
            self.user.groups.clear()


class Invitation(models.Model):
    """A time-limited invitation to join the registry."""
    email = models.EmailField()
    role = models.CharField(max_length=30, blank=True,
                            choices=UserProfile._meta.get_field("role").choices)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="invitations_sent")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="invitations_accepted")

    # 7-day expiry default
    EXPIRY_DAYS = 7

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation for {self.email} ({self.role or 'no role'})"

    @property
    def is_expired(self) -> bool:
        if self.used_at:
            return True
        cutoff = self.created_at + timedelta(days=self.EXPIRY_DAYS)
        return timezone.now() > cutoff

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and self.used_at is None

    def accept(self, user: User) -> None:
        self.used_at = timezone.now()
        self.used_by = user
        self.save(update_fields=["used_at", "used_by"])

    @classmethod
    def create(cls, email: str, role: str, created_by: User | None = None) -> Invitation:
        token = secrets.token_urlsafe(32)
        return cls.objects.create(email=email, role=role, token=token,
                                   created_by=created_by)
