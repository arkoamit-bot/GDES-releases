"""
A small Backup & Restore console inside the Django admin.

Adds superuser-only admin pages to list, create, upload and RESTORE database
backups — so the single-user desktop operator never needs the command line.
Wired into the admin by extending ``admin.site.get_urls`` (imported from
bgddr/urls.py). Restores are guarded: a pre-restore safety snapshot is always
taken, DB connections are closed first, and the operator is told to restart.
"""
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connections
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from bgddr.backup import create_backup, list_backups, restore_from_backup

SQLITE_MAGIC = b"SQLite format 3\x00"


def _superuser(user):
    return user.is_active and user.is_superuser


def _guard(view):
    """Superuser-only + admin styling context."""
    return staff_member_required(view, login_url="admin:login")


def backups_page(request):
    if not _superuser(request.user):
        messages.error(request, "Only a superuser can manage database backups.")
        return HttpResponseRedirect(reverse("admin:index"))
    ctx = {
        **admin.site.each_context(request),
        "title": "Database backups",
        "backups": list_backups(),
        "backup_dir": settings.BACKUP_CONFIG.get("directory"),
        "db_path": str(settings.DATABASES["default"]["NAME"]),
    }
    return render(request, "admin/backups.html", ctx)


@require_POST
def backup_create(request):
    if not _superuser(request.user):
        messages.error(request, "Only a superuser can create backups.")
        return HttpResponseRedirect(reverse("admin:backups"))
    path_ = create_backup(reason="manual")
    if path_:
        messages.success(request, f"Backup created: {path_.name}")
    else:
        messages.error(request, "Backup failed — see Logs/bgddr.log.")
    return HttpResponseRedirect(reverse("admin:backups"))


@require_POST
def backup_upload(request):
    if not _superuser(request.user):
        messages.error(request, "Only a superuser can upload backups.")
        return HttpResponseRedirect(reverse("admin:backups"))
    f = request.FILES.get("backup_file")
    if not f:
        messages.error(request, "Choose a .sqlite3 backup file to upload.")
        return HttpResponseRedirect(reverse("admin:backups"))
    head = f.read(16)
    if head != SQLITE_MAGIC:
        messages.error(request, "That file is not a valid SQLite database.")
        return HttpResponseRedirect(reverse("admin:backups"))
    f.seek(0)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(settings.BACKUP_CONFIG["directory"]) / f"bgddr_backup_{stamp}_uploaded.sqlite3"
    with open(dest, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)
    messages.success(request, f"Uploaded {dest.name}. You can now restore it below.")
    return HttpResponseRedirect(reverse("admin:backups"))


@require_POST
def backup_restore(request):
    if not _superuser(request.user):
        messages.error(request, "Only a superuser can restore the database.")
        return HttpResponseRedirect(reverse("admin:backups"))
    name = (request.POST.get("name") or "").strip()
    if request.POST.get("confirm") != "RESTORE":
        messages.error(request, "Restore not confirmed — type RESTORE to proceed.")
        return HttpResponseRedirect(reverse("admin:backups"))

    target = Path(settings.BACKUP_CONFIG["directory"]) / name
    if not name or not target.exists() or ".." in name or "/" in name or "\\" in name:
        messages.error(request, "Backup not found.")
        return HttpResponseRedirect(reverse("admin:backups"))

    # Release DB handles so the file can be overwritten cleanly, then restore.
    # restore_from_backup() takes a 'pre_restore' safety snapshot first.
    connections.close_all()
    ok = restore_from_backup(target)
    if ok:
        messages.success(
            request,
            f"Database restored from {name}. A pre-restore safety backup was "
            "taken. Please RESTART the application now so the restored data "
            "loads cleanly (you may be logged out).")
    else:
        messages.error(request, "Restore failed — see Logs/bgddr.log.")
    return HttpResponseRedirect(reverse("admin:backups"))


def get_admin_backup_urls():
    """URL patterns to splice into admin.site.get_urls()."""
    return [
        path("backups/", admin.site.admin_view(backups_page), name="backups"),
        path("backups/create/", admin.site.admin_view(backup_create), name="backups_create"),
        path("backups/upload/", admin.site.admin_view(backup_upload), name="backups_upload"),
        path("backups/restore/", admin.site.admin_view(backup_restore), name="backups_restore"),
    ]


def install():
    """Monkey-patch admin.site.get_urls to prepend our backup URLs (once)."""
    if getattr(admin.site, "_bgddr_backup_installed", False):
        return
    original_get_urls = admin.site.get_urls

    def get_urls():
        return get_admin_backup_urls() + original_get_urls()

    admin.site.get_urls = get_urls
    admin.site._bgddr_backup_installed = True
