from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Unidade, ScriptTemplate, ScriptGerado
from .engine import gerar_script


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