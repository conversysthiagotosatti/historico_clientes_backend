from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from zabbix_integration.models import (
    ZabbixHost,
    ZabbixItem,
    ZabbixTrigger,
    ZabbixEvent,
)


class ZabbixTreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente_id = request.query_params.get("cliente")

        if not cliente_id:
            return Response({"detail": "Informe ?cliente=ID"}, status=400)

        hosts = ZabbixHost.objects.filter(cliente_id=cliente_id)

        tree = []

        for host in hosts:
            host_data = {
                "hostid": host.hostid,
                "hostname": getattr(host, "hostname", None),
                "items": []
            }

            # 🔥 ajuste aqui: use o related_name correto
            items = getattr(host, "items", None)

            if items:
                items = items.all()
            else:
                items = ZabbixItem.objects.filter(host=host)

            for item in items:
                item_data = {
                    "itemid": item.itemid,
                    "name": item.name,
                    "triggers": []
                }

                triggers = getattr(item, "triggers", None)

                if triggers:
                    triggers = triggers.all()
                else:
                    triggers = ZabbixTrigger.objects.filter(items=item)

                for trigger in triggers:
                    trigger_data = {
                        "triggerid": trigger.triggerid,
                        "description": getattr(trigger, "description", None),
                        "events": []
                    }

                    events = getattr(trigger, "events", None)

                    if events:
                        events = events.all()
                    else:
                        events = ZabbixEvent.objects.filter(trigger=trigger)

                    for event in events:
                        trigger_data["events"].append({
                            "eventid": event.eventid,
                            "severity": event.severity,
                            "acknowledged": event.acknowledged,
                            "clock": event.clock.isoformat() if event.clock else None,
                        })

                    item_data["triggers"].append(trigger_data)

                host_data["items"].append(item_data)

            tree.append(host_data)

        return Response({
            "cliente": cliente_id,
            "hosts": tree
        })