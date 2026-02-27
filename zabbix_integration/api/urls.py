from django.urls import path
from .views import RelatorioEventosRecoveryAPIView, ZabbixDashboardExecutivoAPIView, SyncHostGroupsAPIView

urlpatterns = [
    path("dashboard/executivo/", ZabbixDashboardExecutivoAPIView.as_view(), name="zabbix-dashboard-executivo",),
    path("sync/hostgroups/", SyncHostGroupsAPIView.as_view()),
    path("relatorio/eventos-recovery/",RelatorioEventosRecoveryAPIView.as_view()),
]