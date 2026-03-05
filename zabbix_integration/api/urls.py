from django.urls import path
from .views import (
    RelatorioEventosRecoveryAPIView,
    ZabbixDashboardExecutivoAPIView,
    SyncHostGroupsAPIView,
    SyncZabbixItemsAPIView,
    SyncZabbixHostsAPIView,
    SyncZabbixHistoryAPIView,
    ZabbixMetricsListAPIView,
)

urlpatterns = [
    path(
        "dashboard/executivo/",
        ZabbixDashboardExecutivoAPIView.as_view(),
        name="zabbix-dashboard-executivo",
    ),
    path("sync/hostgroups/", SyncHostGroupsAPIView.as_view()),
    path("relatorio/eventos-recovery/", RelatorioEventosRecoveryAPIView.as_view()),
    path("sync/items/", SyncZabbixItemsAPIView.as_view(), name="zabbix-sync-items"),
    path("sync/hosts/", SyncZabbixHostsAPIView.as_view(), name="zabbix-sync-hosts"),
    path("sync/history/", SyncZabbixHistoryAPIView.as_view(), name="zabbix-sync-history"),
    path("metrics/", ZabbixMetricsListAPIView.as_view(), name="zabbix-metrics-list"),
]