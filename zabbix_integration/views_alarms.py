from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from zabbix_integration.services.alarms_sync import (
    sync_active_alarms,
    sync_alarm_events,
    sync_alerts_sent,
)

from zabbix_integration.models import ZabbixAlarm, ZabbixAlarmEvent, ZabbixAlertSent
from rest_framework import status

from datetime import datetime, timedelta, timezone
from django.utils.dateparse import parse_datetime


class ZabbixSyncAlarmsView(APIView):
    """
    POST /api/zabbix/sync/alarms/

    Body (opção 1 - intervalo):
    {
      "cliente": 1,
      "data_inicio": "2026-02-01T00:00:00",
      "data_fim": "2026-02-18T23:59:59"
    }

    Body (opção 2 - últimas horas):
    {
      "cliente": 1,
      "since_hours": 24
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente = request.data.get("cliente")

        if not cliente:
            return Response(
                {"detail": "cliente é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data_inicio = request.data.get("data_inicio")
        data_fim = request.data.get("data_fim")
        since_hours = request.data.get("since_hours")

        try:
            if data_inicio and data_fim:
                # 🔎 Usando intervalo de datas
                r1 = sync_active_alarms(
                    int(cliente),
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )

                r2 = sync_alarm_events(
                    int(cliente),
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )

            else:
                # 🔎 Fallback: últimas horas
                since_hours = int(since_hours or 24)

                r1 = sync_active_alarms(
                    int(cliente),
                    since_hours=since_hours,
                )

                r2 = sync_alarm_events(
                    int(cliente),
                    since_hours=since_hours,
                )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "ok",
                "active_alarms": r1,
                "events": r2,
            },
            status=status.HTTP_200_OK,
        )



class ZabbixSyncAlertsSentView(APIView):
    """
    POST /api/zabbix/sync/alerts/
    Body: {"cliente": 1, "since_hours": 24}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente = request.data.get("cliente")
        since_hours = int(request.data.get("since_hours", 24))
        if not cliente:
            return Response({"detail": "cliente é obrigatório"}, status=400)

        r = sync_alerts_sent(int(cliente), since_hours=since_hours)
        return Response({"status": "ok", **r})


class ZabbixAlarmsListView(APIView):
    """
    GET /api/zabbix/alarms/?cliente=1
    Retorna alarmes ATIVOS no seu banco.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente = request.query_params.get("cliente")
        if not cliente:
            return Response({"detail": "Informe ?cliente=ID"}, status=400)

        qs = ZabbixAlarm.objects.filter(cliente_id=int(cliente)).order_by("-clock")[:500]
        data = [
            {
                "eventid": a.eventid,
                "name": a.name,
                "severity": a.severity,
                "acknowledged": a.acknowledged,
                "clock": a.clock.isoformat(),
                "hostid": a.hostid,
                "hostname": a.hostname,
            }
            for a in qs
        ]
        return Response(data)


class ZabbixAlarmEventsListView(APIView):
    """
    GET /api/zabbix/alarm-events/?cliente=1
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente = request.query_params.get("cliente")
        if not cliente:
            return Response({"detail": "Informe ?cliente=ID"}, status=400)

        qs = ZabbixAlarmEvent.objects.filter(cliente_id=int(cliente)).order_by("-clock")[:500]
        data = [
            {
                "eventid": e.eventid,
                "name": e.name,
                "severity": e.severity,
                "acknowledged": e.acknowledged,
                "clock": e.clock.isoformat(),
                "hostid": e.hostid,
                "hostname": e.hostname,
            }
            for e in qs
        ]
        return Response(data)


class ZabbixAlertsSentListView(APIView):
    """
    (Opcional) GET /api/zabbix/alerts-sent/?cliente=1
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente = request.query_params.get("cliente")
        if not cliente:
            return Response({"detail": "Informe ?cliente=ID"}, status=400)

        qs = ZabbixAlertSent.objects.filter(cliente_id=int(cliente)).order_by("-clock")[:500]
        data = [
            {
                "alertid": a.alertid,
                "eventid": a.eventid,
                "clock": a.clock.isoformat(),
                "sendto": a.sendto,
                "subject": a.subject,
                "status": a.status,
            }
            for a in qs
        ]
        return Response(data)


def _resolve_periodo(
    since_hours: int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> tuple[int, int]:
    if data_inicio and data_fim:
        dt_inicio = parse_datetime(data_inicio)
        dt_fim = parse_datetime(data_fim)

        if not dt_inicio or not dt_fim:
            raise ValueError("Formato inválido. Use ISO: 2026-02-01T00:00:00")

        dt_inicio = dt_inicio.astimezone(timezone.utc)
        dt_fim = dt_fim.astimezone(timezone.utc)

        return int(dt_inicio.timestamp()), int(dt_fim.timestamp())

    if since_hours:
        dt_inicio = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)
        return int(dt_inicio.timestamp()), int(datetime.now(tz=timezone.utc).timestamp())

    raise ValueError("Informe since_hours ou data_inicio/data_fim")
