from django.urls import path

from . import views

app_name = "vera_auth"

urlpatterns = [
    path("vera/status/", views.vera_auth_status, name="status"),
    path("vera/open/", views.vera_auth_open, name="open"),
    path("vera/connect/", views.vera_auth_connect, name="connect"),
    path("vera/disconnect/", views.vera_auth_disconnect, name="disconnect"),
    path("vera/complete-review/", views.vera_auth_complete_review, name="complete_review"),
    path("vera/save-response/", views.vera_auth_save_response, name="save_response"),
]
