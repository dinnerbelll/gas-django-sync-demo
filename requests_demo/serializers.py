from rest_framework import serializers

from .models import DemoRequest


class DemoRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoRequest
        fields = (
            "id",
            "student_name",
            "problem_text",
            "submitted_at",
            "raw_payload",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
