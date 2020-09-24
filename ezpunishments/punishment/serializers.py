from rest_framework import serializers

from ezpunishments.core.models import Punishment


class PunishmentSerializer(serializers.ModelSerializer):
    """Serializer for punishment objects"""

    class Meta:
        model = Punishment
        fields = "__all__"
        read_only_fields = (
            "id",
            "mc_uuid",
            "punished_by_uuid",
            "date_punished",
            "last_updated",
        )
