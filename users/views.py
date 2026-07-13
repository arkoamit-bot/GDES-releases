"""
User authentication and profile views for multi-user BGDDR deployment.

Replaces the admin login as the entry point for the guided clinical UI.
Supports: login, logout, password reset, invitation accept, profile edit,
user list (admin), invite user (admin).
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    InvitationAcceptForm, InviteUserForm, LoginForm, ProfileForm)
from .models import Invitation, UserProfile


# --- Helpers -----------------------------------------------------------------

def _is_admin(user):
    return user.is_authenticated and user.is_staff


def _ensure_profile(user: User) -> UserProfile:
    """Create a profile if missing (e.g. for the superuser created via
    createsuperuser before the profile model existed)."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# --- Auth --------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        _ensure_profile(user)
        messages.success(request, f"Welcome, {user.get_full_name() or user.username}.")
        next_url = request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()},
                require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "users/login.html", {"form": form, "active": ""})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("users:login")


# --- Password reset ----------------------------------------------------------

def password_reset_request(request):
    from django.contrib.auth.forms import PasswordResetForm
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # In production this sends an email; in a clinic without email,
            # the admin can trigger the reset manually via the admin UI.
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="users/password_reset_email.txt",
            )
            messages.success(
                request,
                "If an account with that email exists, a password reset link "
                "has been sent. Check with your administrator if email is not "
                "available.")
            return redirect("users:login")
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_request.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    from django.contrib.auth.views import PasswordResetConfirmView
    # Delegate to Django's built-in view with our template
    return PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html",
        success_url="/login/",
    )(request, uidb64=uidb64, token=token)


# --- Invitation accept -------------------------------------------------------

def invitation_accept(request, token):
    invitation = get_object_or_404(Invitation, token=token)
    if not invitation.is_valid:
        messages.error(request, "This invitation has expired or already been used.")
        return redirect("users:login")

    if request.method == "POST":
        # Build an *unsaved* user, validate the password form, and only persist
        # once valid — so a failed submission never leaves an orphaned account.
        username = invitation.email.split("@")[0]
        base = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User(
            username=username, email=invitation.email,
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
        )
        form = InvitationAcceptForm(user, data=request.POST)
        if form.is_valid():
            form.save()   # sets the password and saves the user
            profile = UserProfile.objects.create(
                user=user, role=invitation.role, is_clinician=True)
            invitation.accept(user)
            login(request, user)
            messages.success(
                request,
                f"Account created. You are assigned the '{profile.get_role_display()}' role.")
            return redirect("dashboard")
    else:
        form = InvitationAcceptForm(user=None)
        form.user = None  # will be set on POST

    return render(request, "users/invitation_accept.html",
                  {"form": form, "invitation": invitation, "active": ""})


# --- Profile -----------------------------------------------------------------

@login_required
def profile_view(request):
    profile = _ensure_profile(request.user)
    form = ProfileForm(request.POST or None, instance=profile, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("users:profile")
    return render(request, "users/profile.html",
                  {"form": form, "profile": profile, "active": ""})


# --- Admin: user list & invite ----------------------------------------------

@user_passes_test(_is_admin)
def user_list(request):
    users = (User.objects.select_related("profile")
             .prefetch_related("groups")
             .order_by("-date_joined"))
    invitations = (Invitation.objects
                   .filter(used_at__isnull=True, created_at__gte=timezone.now() - timezone.timedelta(days=7))
                   .order_by("-created_at"))
    return render(request, "users/user_list.html",
                  {"users": users, "invitations": invitations, "active": ""})


@user_passes_test(_is_admin)
def invite_user(request):
    form = InviteUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        inv = form.create_invitation(created_by=request.user)
        # Build the invitation URL for the admin to copy/share
        accept_url = request.build_absolute_uri(
            reverse("users:invitation_accept", kwargs={"token": inv.token}))
        messages.success(
            request,
            f"Invitation created for {inv.email}. Share this link: {accept_url}")
        return redirect("users:user_list")
    return render(request, "users/invite_user.html",
                  {"form": form, "active": ""})
