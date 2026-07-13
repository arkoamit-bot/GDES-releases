"""
User-facing forms: login, password reset, invitation accept, profile edit.
"""
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Invitation, UserProfile


class LoginForm(AuthenticationForm):
    """Styled login form (replaces the admin login for the guided UI)."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Username",
            "autocomplete": "username",
        }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Password",
            "autocomplete": "current-password",
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["invalid_login"] = (
            "Please enter a correct username and password. "
            "Note that both fields may be case-sensitive.")


class InvitationAcceptForm(SetPasswordForm):
    """Set password when accepting an invitation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"

    def clean(self):
        cleaned = super().clean()
        # Validate password strength
        password = cleaned.get("new_password1")
        if password and len(password) < 8:
            self.add_error("new_password1", "Password must be at least 8 characters.")
        return cleaned


class ProfileForm(forms.ModelForm):
    """Edit the user's own profile (name, email, department, phone)."""
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "input"}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "input"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "input"}))

    class Meta:
        model = UserProfile
        fields = ["department", "phone"]
        widgets = {
            "department": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self._user:
            self._user.first_name = self.cleaned_data.get("first_name", "")
            self._user.last_name = self.cleaned_data.get("last_name", "")
            self._user.email = self.cleaned_data.get("email", "")
            if commit:
                self._user.save()
        return profile


class InviteUserForm(forms.Form):
    """Admin-only form to invite a new user."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "doctor@birdem.org"}))
    role = forms.ChoiceField(
        choices=UserProfile._meta.get_field("role").choices,
        widget=forms.Select(attrs={"class": "input"}))
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "First name"}))
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Last name"}))

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        if Invitation.objects.filter(email__iexact=email, used_at__isnull=True).exists():
            raise ValidationError("An active invitation already exists for this email.")
        return email

    def create_invitation(self, created_by) -> Invitation:
        return Invitation.create(
            email=self.cleaned_data["email"],
            role=self.cleaned_data["role"],
            created_by=created_by,
        )
