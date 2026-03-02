from rest_framework import serializers
from .models import SoftdeskChamado


class SoftdeskChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftdeskChamado
        fields = "__all__"