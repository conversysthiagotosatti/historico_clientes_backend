from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import PodeGerenciarEquipe

from .models_equipes import Equipe, EquipeMembro
from .serializers_equipes import EquipeSerializer, EquipeMembroSerializer


class EquipeViewSet(ModelViewSet):
    queryset = Equipe.objects.all().prefetch_related("membros", "contratos")
    serializer_class = EquipeSerializer
    permission_classes = [IsAuthenticated, PodeGerenciarEquipe]

    @action(detail=True, methods=["post"], url_path="add-membro")
    def add_membro(self, request, pk=None):
        equipe = self.get_object()
        payload = {
            "equipe": equipe.id,
            "user": request.data.get("user"),
            "papel": request.data.get("papel", "MEMBRO"),
            "ativo": request.data.get("ativo", True),
        }
        ser = EquipeMembroSerializer(data=payload)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="set-lider")
    def set_lider(self, request, pk=None):
        equipe = self.get_object()
        user_id = request.data.get("user")
        if not EquipeMembro.objects.filter(equipe=equipe, user_id=user_id).exists():
            return Response({"detail": "Usuário deve ser membro da equipe."}, status=400)
        equipe.lider_id = int(user_id)
        equipe.save(update_fields=["lider", "atualizado_em"])
        return Response({"ok": True, "lider": equipe.lider_id})

    @action(detail=True, methods=["post"], url_path="set-gerente")
    def set_gerente(self, request, pk=None):
        equipe = self.get_object()
        user_id = request.data.get("user")
        if not EquipeMembro.objects.filter(equipe=equipe, user_id=user_id).exists():
            return Response({"detail": "Usuário deve ser membro da equipe."}, status=400)
        equipe.gerente_id = int(user_id)
        equipe.save(update_fields=["gerente", "atualizado_em"])
        return Response({"ok": True, "gerente": equipe.gerente_id})
    
    def get_queryset(self):
        qs = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)

        if profile and profile.tipo_usuario == "CLIENTE":
            return qs.filter(contratos__cliente_id=profile.cliente_id).distinct()

        return qs


class EquipeMembroViewSet(ModelViewSet):
    queryset = EquipeMembro.objects.all().select_related("equipe", "user")
    serializer_class = EquipeMembroSerializer
    permission_classes = [IsAuthenticated, PodeGerenciarEquipe]
