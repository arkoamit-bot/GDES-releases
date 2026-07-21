"""Help / documentation views."""
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render

from ._common import login_required


@login_required
def help_index(request):
    return render(request, "help/index.html", {"active": "help"})


@login_required
def help_user(request):
    return render(request, "help/user.html", {"active": "help"})


@login_required
def help_admin(request):
    if not request.user.is_staff:
        messages.error(request, "The administrator guide is available to staff accounts only.")
        return redirect("clinic:help")
    return render(request, "help/admin.html", {"active": "help"})


@login_required
def help_developer(request):
    if not request.user.is_superuser:
        messages.error(request, "The developer guide is available to the maintainer (superuser) only.")
        return redirect("clinic:help")
    return render(request, "help/developer.html", {"active": "help"})
