import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from helpdesk.models import (
    Categoria, Servico, TipoChamado, Area, Impacto, PrioridadeHelpdesk,
    ClienteHelpdesk, ContratoHelpdesk, TemplateChamado, ItemConfiguracao, 
    Filial, Departamento, Atendente, UsuarioHelpdesk, StatusChamadoConfig
)

# Softdesk Constants
BASE_URL = "https://conversys.soft4.com.br/api/api.php"

class Command(BaseCommand):
    help = "Sincroniza os dados mestres (Categorias, Clientes, CIs...) do Softdesk para o banco local."

    def get_token(self):
        # Fallback to the token provided by the user if not in settings
        return getattr(settings, 'SOFTDESK_HASH_API', 'lHasHE8fA1MeujVMB7nQKzoAqzJrdhiRSgHz3fNfbguJnAn0W3KU59k40wpWX1uW')

    def fetch_data(self, endpoint):
        token = self.get_token()
        headers = {
            'hash-api': token,
            'Accept': 'application/json'
        }
        # Disable SSL verification temporary because it was causing issues for the user in curl
        res = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, verify=False)
        if res.status_code == 200:
            data = res.json()
            return data.get('objeto', [])
        else:
            self.stdout.write(self.style.ERROR(f"Erro ao buscar {endpoint}: {res.status_code} - {res.text}"))
            return []

    def handle(self, *args, **options):
        self.stdout.write("Iniciando sincronização com a API do Softdesk...")

        # 1. Categorias
        self.stdout.write("Sincronizando Categorias...")
        categorias = self.fetch_data('categoria')
        for cat in categorias:
            Categoria.objects.update_or_create(
                codigo_integracao=cat.get('codigo'),
                defaults={'nome': cat.get('descricao', f"Cat {cat.get('codigo')}")}
            )

        # 2. Serviços
        self.stdout.write("Sincronizando Serviços...")
        servicos = self.fetch_data('servico')
        for serv in servicos:
            cat_obj = None
            cat_data = serv.get('categoria')
            if cat_data and isinstance(cat_data, dict) and cat_data.get('codigo'):
                cat_obj = Categoria.objects.filter(codigo_integracao=cat_data['codigo']).first()
                
            Servico.objects.update_or_create(
                codigo_integracao=serv.get('codigo'),
                defaults={
                    'nome': serv.get('descricao', f"Serv {serv.get('codigo')}"),
                    'categoria': cat_obj
                }
            )

        # 3. Tipos de Chamado
        self.stdout.write("Sincronizando Tipos de Chamado...")
        tipos = self.fetch_data('tipo-chamado')
        for t in tipos:
            TipoChamado.objects.update_or_create(
                codigo_integracao=t.get('codigo'),
                defaults={'nome': t.get('descricao', '')}
            )

        # 4. Áreas
        self.stdout.write("Sincronizando Áreas...")
        areas = self.fetch_data('area')
        for a in areas:
            Area.objects.update_or_create(
                codigo_integracao=a.get('codigo'),
                defaults={'nome': a.get('descricao', '')}
            )

        # 5. Impactos (Nível de Indisponibilidade)
        self.stdout.write("Sincronizando Impactos...")
        impactos = self.fetch_data('nivel-indisponibilidade')
        for i in impactos:
            Impacto.objects.update_or_create(
                codigo_integracao=i.get('codigo'),
                defaults={'nome': i.get('descricao', '')}
            )

        # 6. Prioridades
        self.stdout.write("Sincronizando Prioridades...")
        prioridades = self.fetch_data('prioridade')
        for p in prioridades:
            PrioridadeHelpdesk.objects.update_or_create(
                codigo_integracao=p.get('codigo'),
                defaults={'nome': p.get('descricao', '')}
            )

        # 7. Clientes
        self.stdout.write("Sincronizando Clientes...")
        clientes = self.fetch_data('cliente')
        for c in clientes:
            nome_cliente = c.get('nome', '')[:255]
            ClienteHelpdesk.objects.update_or_create(
                codigo_integracao=c.get('codigo'),
                defaults={'razao_social': nome_cliente, 'nome_fantasia': nome_cliente}
            )

        # 8. Contratos
        self.stdout.write("Sincronizando Contratos...")
        contratos = self.fetch_data('contrato')
        for c in contratos:
            cliente_obj = None
            contratante = c.get('contratante')
            if contratante and isinstance(contratante, dict) and contratante.get('codigo'):
                cliente_obj = ClienteHelpdesk.objects.filter(codigo_integracao=contratante['codigo']).first()
                
            ContratoHelpdesk.objects.update_or_create(
                codigo_integracao=c.get('codigo'),
                defaults={
                    'numero': c.get('numero', ''),
                    'descricao': c.get('titulo', ''),
                    'cliente': cliente_obj
                }
            )

        # 9. Templates
        self.stdout.write("Sincronizando Templates de Chamado...")
        templates = self.fetch_data('template-chamado')
        for t in templates:
            cat_obj = None
            serv_obj = None
            if t.get('categoria') and isinstance(t.get('categoria'), dict):
                cat_obj = Categoria.objects.filter(codigo_integracao=t['categoria'].get('codigo')).first()
            if t.get('servico') and isinstance(t.get('servico'), dict):
                serv_obj = Servico.objects.filter(codigo_integracao=t['servico'].get('codigo')).first()
                
            TemplateChamado.objects.update_or_create(
                codigo_integracao=t.get('codigo'),
                defaults={
                    'nome': t.get('nome') or t.get('descricao') or f"Template {t.get('codigo')}",
                    'categoria': cat_obj,
                    'servico': serv_obj
                }
            )

        # 10. Item Configuração (CIs)
        self.stdout.write("Sincronizando Itens de Configuração (CIs)...")
        # To avoid rate limits or timeouts, just get the first page if pagination exists, but the user said they got 7000. 
        # For this script we will fetch the payload as is.
        cis = self.fetch_data('item-configuracao')
        for ci in cis:
            ItemConfiguracao.objects.update_or_create(
                codigo_integracao=ci.get('codigo'),
                defaults={
                    'nome': ci.get('nome', ''),
                    'numero_serie': ci.get('numero_serie', '')[:100],  # trim to max length
                    'descricao': ci.get('descricao', '')
                }
            )

        self.stdout.write(self.style.SUCCESS("Sincronização com Softdesk concluída com sucesso!"))
