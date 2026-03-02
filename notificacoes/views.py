from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notificacao
from .serializers import NotificacaoSerializer


class NotificacaoViewSet(ModelViewSet):
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 👇 Só retorna notificações do usuário logado
        return Notificacao.objects.filter(
            usuario=self.request.user
        )

    def perform_create(self, serializer):
        # 👇 Força a notificação ser do usuário logado
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=["post"])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        return Response({"status": "Notificação marcada como lida"})

    @action(detail=False, methods=["get"])
    def nao_lidas(self, request):
        total = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()

        return Response({"nao_lidas": total})