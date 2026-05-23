from django.urls import path

from .views import DemoRequestCreateAPIView


app_name = "requests_demo"

urlpatterns = [
    path("requests/", DemoRequestCreateAPIView.as_view(), name="request-create"),
]
