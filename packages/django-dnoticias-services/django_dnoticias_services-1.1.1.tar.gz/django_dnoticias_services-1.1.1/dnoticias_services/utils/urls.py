from django.urls import path

from . import views


urlpatterns = [
    path("healthcheck/", views.HealthCheckView.as_view(), name="healthcheck"),
    path("readiness/", views.ReadinessCheckView.as_view(), name="readiness"),
]
