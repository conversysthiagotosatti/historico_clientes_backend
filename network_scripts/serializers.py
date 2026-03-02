from rest_framework import serializers
from .models import (
    Organization,
    Unidade,
    Link,
    ScriptTemplate,
    ScriptGerado
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = "__all__"


class UnidadeSerializer(serializers.ModelSerializer):
    link = LinkSerializer()

    class Meta:
        model = Unidade
        fields = "__all__"

    def create(self, validated_data):
        link_data = validated_data.pop("link")
        unidade = Unidade.objects.create(**validated_data)
        Link.objects.create(unidade=unidade, **link_data)
        return unidade


class ScriptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptTemplate
        fields = "__all__"


class ScriptGeradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptGerado
        fields = "__all__"