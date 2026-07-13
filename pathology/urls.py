from django.urls import path

from . import views

app_name = "pathology"

urlpatterns = [
    path("biopsy/<int:pk>/review/", views.biopsy_review, name="biopsy_review"),
    path("discordant/", views.discordant, name="discordant"),
    path("agreement/", views.agreement, name="agreement"),
]
