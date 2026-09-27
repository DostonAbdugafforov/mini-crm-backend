from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet, DashboardStatsView

router = DefaultRouter()
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"dashboard/stats", DashboardStatsView, basename="dashboard-stats")

urlpatterns = [
    path("", include(router.urls)),
]