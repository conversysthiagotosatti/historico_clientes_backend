from rest_framework.viewsets import ModelViewSet
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all().order_by("-criado_em")
    serializer_class = ClienteSerializer
