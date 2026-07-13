from django.contrib import admin
from .models import DecisionRequest, DecisionResult


@admin.register(DecisionRequest)
class DecisionRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "patient", "encounter", "created_at"]


@admin.register(DecisionResult)
class DecisionResultAdmin(admin.ModelAdmin):
    list_display = ["request", "phenotype", "urgency_level"]
