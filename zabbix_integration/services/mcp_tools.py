from zabbix_integration.services.dashboards import dashboard_executivo
from zabbix_integration.services.reports import relatorio_incidentes


def tool_dashboard_executivo(cliente_id: int):
    return dashboard_executivo(cliente_id)


def tool_relatorio_incidentes(cliente_id: int, dias: int = 30):
    return relatorio_incidentes(cliente_id, dias)