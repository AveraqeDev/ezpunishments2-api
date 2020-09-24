from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register("punishments", views.PunishmentViewSet)

app_name = "punishment"

urlpatterns = [
    path("", include(router.urls)),
]
