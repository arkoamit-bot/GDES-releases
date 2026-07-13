from django.urls import path

from . import views

app_name = "treatments"

urlpatterns = [
    path("drug-interactions/check/", views.drug_interactions_check,
         name="drug-interactions-check"),
    path("drug-contraindications/check/", views.drug_contraindications_check,
         name="drug-contraindications-check"),
]
