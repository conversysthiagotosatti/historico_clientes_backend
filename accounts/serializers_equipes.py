from rest_framework import serializers
from .models_equipes import Equipe, EquipeMembro


class EquipeMembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipeMembro
        fields = ["id", "equipe", "user", "papel", "ativo", "criado_em"]
        read_only_fields = ["id", "criado_em"]


class EquipeSerializer(serializers.ModelSerializer):
    membros = EquipeMembroSerializer(many=True, read_only=True)

    # ✅ leitura: lista de ids
    contratos = serializers.SerializerMethodField()

    # ✅ escrita: lista de ids
    contratos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="Lista de IDs de contratos para vincular à equipe.",
    )

    class Meta:
        model = Equipe
        fields = [
            "id", "nome", "descricao",
            "contratos", "contratos_ids",
            "lider", "gerente",
            "membros",
            "criado_em", "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def get_contratos(self, obj):
        return list(obj.contratos.values_list("id", flat=True))

    def _set_contratos(self, instance: Equipe, contratos_ids):
        from contratos.models import Contrato  # import local evita circular
        qs = Contrato.objects.filter(id__in=contratos_ids)
        instance.contratos.set(qs)

    def create(self, validated_data):
        contratos_ids = validated_data.pop("contratos_ids", None)
        instance = super().create(validated_data)
        if contratos_ids is not None:
            self._set_contratos(instance, contratos_ids)
        return instance

    def update(self, instance, validated_data):
        contratos_ids = validated_data.pop("contratos_ids", None)
        instance = super().update(instance, validated_data)
        if contratos_ids is not None:
            self._set_contratos(instance, contratos_ids)
        return instance
