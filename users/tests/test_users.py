"""User profile / group-sync tests."""
from django.contrib.auth.models import Group, User
from django.test import TestCase

from ..models import UserProfile


class ProfileGroupSyncTests(TestCase):
    def test_extra_permission_group_survives_a_profile_save(self):
        extra = Group.objects.create(name="audit_reader")
        user = User.objects.create_user("u1", password="x")
        user.groups.add(Group.objects.create(name="coordinator"), extra)

        profile = UserProfile.objects.create(user=user, role="coordinator")
        names = set(user.groups.values_list("name", flat=True))
        self.assertIn("coordinator", names)
        # A second save must not replace the whole group set.
        profile.phone = "01700000000"
        profile.save()
        names = set(user.groups.values_list("name", flat=True))
        self.assertIn("coordinator", names)
        self.assertIn("audit_reader", names)

    def test_blank_role_keeps_non_role_groups(self):
        extra = Group.objects.create(name="site_helper")
        user = User.objects.create_user("u2", password="x")
        user.groups.add(extra)

        # role="" is the field default and is what _ensure_profile() produces
        # on a user's first login; it used to clear() every group.
        UserProfile.objects.create(user=user, role="")
        self.assertIn("site_helper", set(user.groups.values_list("name", flat=True)))

    def test_changing_role_replaces_the_previous_role_group(self):
        user = User.objects.create_user("u3", password="x")
        profile = UserProfile.objects.create(user=user, role="coordinator")
        self.assertIn("coordinator", set(user.groups.values_list("name", flat=True)))

        profile.role = "pathologist"
        profile.save()
        names = set(user.groups.values_list("name", flat=True))
        self.assertIn("pathologist", names)
        self.assertNotIn("coordinator", names)

    def test_clearing_the_role_removes_only_the_role_group(self):
        extra = Group.objects.create(name="stats")
        user = User.objects.create_user("u4", password="x")
        profile = UserProfile.objects.create(user=user, role="readonly")
        user.groups.add(extra)

        profile.role = ""
        profile.save()
        names = set(user.groups.values_list("name", flat=True))
        self.assertNotIn("readonly", names)
        self.assertIn("stats", names)
