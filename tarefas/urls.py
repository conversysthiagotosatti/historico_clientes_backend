from rest_framework.routers import DefaultRouter
from .views import TarefaViewSet, ApontamentoViewSet

router = DefaultRouter()
router.register(r"tarefas", TarefaViewSet, basename="tarefas")
router.register(r"apontamentos", ApontamentoViewSet, basename="apontamentos")

urlpatterns = router.urls
