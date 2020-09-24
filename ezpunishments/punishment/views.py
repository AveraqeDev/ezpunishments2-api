from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from ezpunishments.core.models import Punishment
from . import serializers


class PunishmentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PunishmentSerializer
    queryset = Punishment.objects.all()
    authentication__classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        mc_usernames = self.request.query_params.get("mc_username")
        punished_by = self.request.query_params.get("punished_by")
        queryset = self.queryset
        if mc_usernames:
            queryset = queryset.filter(mc_username__in=mc_usernames)
        if punished_by:
            queryset = queryset.filter(punished_by__in=punished_by)

        return queryset
