from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", views.password_reset_request, name="password_reset"),
    # Django's built-in password reset confirm (we wrap it in our template)
    path("password-reset-confirm/<uidb64>/<token>/",
         views.password_reset_confirm, name="password_reset_confirm"),
    path("invitation/<str:token>/", views.invitation_accept, name="invitation_accept"),
    path("profile/", views.profile_view, name="profile"),
    path("users/", views.user_list, name="user_list"),
    path("users/invite/", views.invite_user, name="invite_user"),
]