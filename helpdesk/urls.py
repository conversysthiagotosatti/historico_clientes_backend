from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SetorViewSet, ChamadoViewSet, ChamadoTimerViewSet

router = DefaultRouter()
router.register(r'setores', SetorViewSet, basename='setor')
router.register(r'chamados', ChamadoViewSet, basename='chamado')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom Timer Actions under /helpdesk/timers/<chamado_id>/<action>/
    path('timers/<int:pk>/start/', ChamadoTimerViewSet.as_view({'post': 'start'}), name='timer-start'),
    path('timers/<int:pk>/pause/', ChamadoTimerViewSet.as_view({'post': 'pause'}), name='timer-pause'),
    path('timers/<int:pk>/finalizar/', ChamadoTimerViewSet.as_view({'post': 'finalizar_apontamento'}), name='timer-finalizar'),
]
