from django.urls import path

from . import views

app_name = "prescriptions"

urlpatterns = [
    path("<int:pk>/preview/", views.preview, name="preview"),
    path("<int:pk>/html/", views.html_download, name="html_download"),
    path("<int:pk>/reconcile/preview/", views.reconcile_preview, name="reconcile_preview"),
    path("<int:pk>/finalize/", views.finalize, name="finalize"),
    path("<int:pk>/pdf/", views.pdf, name="pdf"),
]
