from django.urls import path

from . import views

app_name = "exports"

urlpatterns = [
    path("", views.export_index, name="export-index"),
    path("csv/", views.export_dataset_csv, name="export-csv"),
    path("xlsx/", views.export_dataset_xlsx, name="export-xlsx"),
    path("sav/", views.export_dataset_sav, name="export-sav"),
]
