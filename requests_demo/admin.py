from django.contrib import admin

from .models import DemoRequest


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "student_name", "submitted_at", "created_at")
    list_filter = ("submitted_at", "created_at")
    search_fields = ("student_name", "problem_text")
    readonly_fields = ("created_at",)
