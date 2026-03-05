from rest_framework.routers import DefaultRouter
from .views import TarefaViewSet, ApontamentoViewSet, EpicoViewSet

router = DefaultRouter()
router.register(r"tarefas", TarefaViewSet, basename="tarefas")
router.register(r"apontamentos", ApontamentoViewSet, basename="apontamentos")
router.register(r"epicos", EpicoViewSet, basename="epicos")

urlpatterns = router.urls
