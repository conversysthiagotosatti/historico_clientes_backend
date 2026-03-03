from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Unidade, ScriptTemplate, ScriptGerado
from .engine import gerar_script
from config.services import gerar_token_graph, enviar_email_graph


class GerarScriptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        unidade_id = request.data.get("unidade_id")
        template_id = request.data.get("template_id")

        unidade = get_object_or_404(Unidade, id=unidade_id)
        template = get_object_or_404(ScriptTemplate, id=template_id)

        script = gerar_script(unidade, template)

        script_obj = ScriptGerado.objects.create(
            unidade=unidade,
            template=template,
            script=script,
            gerado_por=request.user,
        )

        return Response({
            "script": script_obj.script,
            "hash": script_obj.hash_script,
            "gerado_em": script_obj.gerado_em,
        })

class TestarTokenGraphView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token_data = gerar_token_graph()

        return Response({
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "access_token_inicio": token_data.get("access_token")[:50]
        })

class TestarEnvioEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        enviar_email_graph(
            destinatario="thiago.tosatti@conversys.global",
            assunto="Teste envio via Graph",
            corpo="Funcionando via Microsoft Graph 🚀"
        )

        return Response({"status": "Email enviado"})