from django.http import JsonResponse
from django.contrib import admin
from django.urls import include, path


def health_check(request):
    return JsonResponse({"ok": True})


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("api/demo/", include("requests_demo.urls")),
]
