from django.urls import path

from . import views

app_name = "exports"

urlpatterns = [
    path("research-dataset/", views.research_dataset, name="research_dataset"),
    path("data-dictionary/", views.dictionary, name="data_dictionary"),
]
