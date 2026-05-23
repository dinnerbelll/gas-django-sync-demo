import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission


class HasDemoApiKey(BasePermission):
    message = "Invalid API key."

    def has_permission(self, request, view):
        expected_key = settings.DEMO_API_KEY
        provided_key = request.headers.get("X-DEMO-API-KEY", "")

        if not expected_key or not provided_key:
            return False

        return hmac.compare_digest(provided_key, expected_key)
