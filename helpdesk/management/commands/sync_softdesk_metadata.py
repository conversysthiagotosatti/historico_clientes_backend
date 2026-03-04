import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from helpdesk.models import (
    Categoria, Servico, TipoChamado, Area, Impacto, PrioridadeHelpdesk,
    ClienteHelpdesk, ContratoHelpdesk, TemplateChamado, ItemConfiguracao,
    CampoCustomizavelIC, Filial, Departamento, Atendente, UsuarioHelpdesk,
    StatusChamadoConfig, GrupoSolucao, TemaTemplate, Cidade, Empresa,
    Fornecedor, CentroCusto, FAQ,
)

BASE_URL = "https://conversys.soft4.com.br/api/api.php"


class Command(BaseCommand):
    help = "Sincroniza TODOS os dados mestres do Softdesk para o banco local."

    def get_token(self):
        return getattr(
            settings, 'SOFTDESK_HASH_API',
            'lHasHE8fA1MeujVMB7nQKzoAqzJrdhiRSgHz3fNfbguJnAn0W3KU59k40wpWX1uW'
        )

    def fetch(self, endpoint):
        """Busca dados de um endpoint do Softdesk e retorna lista de objetos."""
        try:
            res = requests.get(
                f"{BASE_URL}/{endpoint}",
                headers={'hash-api': self.get_token(), 'Accept': 'application/json'},
                verify=False, timeout=120
            )
            if res.status_code == 200:
                data = res.json()
                objetos = data.get('objeto', [])
                if isinstance(objetos, list):
                    return objetos
                # Caso retorne objeto único, embrulha em lista
                return [objetos] if objetos else []
            self.stderr.write(f"  ✗ {endpoint}: HTTP {res.status_code}")
            return []
        except Exception as e:
            self.stderr.write(f"  ✗ {endpoint}: {e}")
            return []

    def _count(self, label, items):
        """Log helper — imprime qtd sincronizada."""
        self.stdout.write(f"  ✓ {label}: {len(items)} registros")

    # ── helpers para FK lookup ──
    def _fk(self, Model, data, key='codigo'):
        """Resolve FK via codigo_integracao."""
        if data and isinstance(data, dict) and data.get(key):
            return Model.objects.filter(codigo_integracao=data[key]).first()
        return None

    # ──────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "═══ Sincronização completa Softdesk → Django ═══"
        ))

        # ── 1. Cidade (dependência de Empresa, Cliente, Filial, Fornecedor) ──
        items = self.fetch('cidade')
        for x in items:
            Cidade.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or '')[:200],
                    'estado': (x.get('estado') or '')[:100],
                }
            )
        self._count("Cidade", items)

        # ── 2. Empresa ──
        items = self.fetch('empresa')
        for x in items:
            Empresa.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'razao_social': (x.get('razao_social') or x.get('nome') or '')[:255],
                    'nome_fantasia': (x.get('nome_fantasia') or '')[:255],
                    'cnpj': (x.get('cnpj') or '')[:20],
                    'cidade': self._fk(Cidade, x.get('cidade')),
                }
            )
        self._count("Empresa", items)

        # ── 3. Departamento ──
        items = self.fetch('departamento')
        for x in items:
            Departamento.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or x.get('nome') or '')[:200]}
            )
        self._count("Departamento", items)

        # ── 4. Cliente ──
        items = self.fetch('cliente')
        for x in items:
            nome = (x.get('nome') or x.get('razao_social') or '')[:255]
            ClienteHelpdesk.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'razao_social': nome,
                    'nome_fantasia': (x.get('nome_fantasia') or nome)[:255],
                    'cnpj': (x.get('cnpj') or '')[:20],
                    'cpf': (x.get('cpf') or '')[:15],
                    'email': (x.get('email') or '')[:254] or None,
                    'telefone': (x.get('telefone') or '')[:30],
                    'cidade': self._fk(Cidade, x.get('cidade')),
                    'empresa': self._fk(Empresa, x.get('empresa')),
                }
            )
        self._count("Cliente", items)

        # ── 5. Filial ──
        items = self.fetch('filial')
        for x in items:
            Filial.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or x.get('razao_social') or x.get('descricao') or '')[:200],
                    'telefone': (x.get('telefone') or '')[:30],
                    'email': (x.get('email') or '')[:254] or None,
                    'cliente': self._fk(ClienteHelpdesk, x.get('cliente')),
                    'cidade': self._fk(Cidade, x.get('cidade')),
                }
            )
        self._count("Filial", items)

        # ── 6. Usuário ──
        items = self.fetch('usuario')
        for x in items:
            UsuarioHelpdesk.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or '')[:200],
                    'login': (x.get('login') or '')[:100],
                    'email': (x.get('email') or '')[:254] or None,
                    'telefone': (x.get('telefone') or '')[:30],
                    'cliente': self._fk(ClienteHelpdesk, x.get('cliente')),
                    'filial': self._fk(Filial, x.get('filial')),
                    'departamento': self._fk(Departamento, x.get('departamento')),
                }
            )
        self._count("Usuário", items)

        # ── 7. Contrato ──
        items = self.fetch('contrato')
        for x in items:
            ContratoHelpdesk.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'numero': (x.get('numero') or '')[:100],
                    'descricao': x.get('titulo') or x.get('descricao') or '',
                    'cliente': self._fk(ClienteHelpdesk, x.get('contratante') or x.get('cliente')),
                    'fornecedor': self._fk(Fornecedor, x.get('fornecedor')),
                }
            )
        self._count("Contrato", items)

        # ── 8. Atendente ──
        items = self.fetch('atendente')
        for x in items:
            Atendente.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or '')[:200],
                    'email': (x.get('email') or '')[:254] or None,
                }
            )
        self._count("Atendente", items)

        # ── 9. Categoria ──
        items = self.fetch('categoria')
        for x in items:
            Categoria.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Categoria", items)

        # ── 10. Serviço ──
        items = self.fetch('servico')
        for x in items:
            Servico.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('descricao') or '')[:200],
                    'categoria': self._fk(Categoria, x.get('categoria')),
                }
            )
        self._count("Serviço", items)

        # ── 11. Tipo de Chamado ──
        items = self.fetch('tipo-chamado')
        for x in items:
            TipoChamado.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Tipo Chamado", items)

        # ── 12. Área ──
        items = self.fetch('area')
        for x in items:
            Area.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Área", items)

        # ── 13. Impacto / Nível de Indisponibilidade ──
        items = self.fetch('nivel-indisponibilidade')
        for x in items:
            Impacto.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Impacto", items)

        # ── 14. Prioridade ──
        items = self.fetch('prioridade')
        for x in items:
            PrioridadeHelpdesk.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:100]}
            )
        self._count("Prioridade", items)

        # ── 15. Status de Chamado ──
        items = self.fetch('status-chamado')
        for x in items:
            StatusChamadoConfig.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:100]}
            )
        self._count("Status Chamado", items)

        # ── 16. Grupo de Solução (= "Setor" no nosso app) ──
        items = self.fetch('grupo-solucao')
        for x in items:
            GrupoSolucao.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Grupo Solução", items)

        # ── 17. Tema de Template ──
        items = self.fetch('tema-template')
        for x in items:
            TemaTemplate.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={'nome': (x.get('descricao') or '')[:200]}
            )
        self._count("Tema Template", items)

        # ── 18. Template de Chamado ──
        items = self.fetch('template-chamado')
        for x in items:
            TemplateChamado.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or x.get('descricao') or '')[:200],
                    'categoria': self._fk(Categoria, x.get('categoria')),
                    'servico': self._fk(Servico, x.get('servico')),
                    'tema': self._fk(TemaTemplate, x.get('tema')),
                }
            )
        self._count("Template Chamado", items)

        # ── 19. Item de Configuração (CIs) ──
        items = self.fetch('item-configuracao')
        for x in items:
            ItemConfiguracao.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('nome') or '')[:255],
                    'numero_serie': (x.get('numero_serie') or '')[:100],
                    'descricao': x.get('descricao') or '',
                }
            )
        self._count("Item Configuração", items)

        # ── 20. Campos Customizáveis de IC ──
        items = self.fetch('campo-customizavel-ic')
        for x in items:
            CampoCustomizavelIC.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('descricao') or x.get('nome') or '')[:200],
                }
            )
        self._count("Campo Custom. IC", items)

        # ── 21. Fornecedor ──
        items = self.fetch('fornecedor')
        for x in items:
            nome = (x.get('razao_social') or x.get('nome') or '')[:255]
            Fornecedor.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'razao_social': nome,
                    'nome_fantasia': (x.get('nome_fantasia') or '')[:255],
                    'cnpj': (x.get('cnpj') or '')[:20],
                    'email': (x.get('email') or '')[:254] or None,
                    'telefone': (x.get('telefone') or '')[:30],
                    'cidade': self._fk(Cidade, x.get('cidade')),
                    'area': self._fk(Area, x.get('area')),
                }
            )
        self._count("Fornecedor", items)

        # ── 22. Centro de Custo ──
        items = self.fetch('centro-custo')
        for x in items:
            CentroCusto.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'nome': (x.get('descricao') or x.get('nome') or '')[:200],
                    'codigo': (x.get('codigo_centro') or str(x.get('codigo', '')))[:50],
                }
            )
        self._count("Centro Custo", items)

        # ── 23. FAQ / Base de Conhecimento ──
        items = self.fetch('faq')
        for x in items:
            FAQ.objects.update_or_create(
                codigo_integracao=x.get('codigo'),
                defaults={
                    'titulo': (x.get('titulo') or x.get('descricao') or '')[:255],
                    'conteudo': x.get('conteudo') or x.get('resposta') or '',
                }
            )
        self._count("FAQ", items)

        # ── DONE ──
        self.stdout.write(self.style.SUCCESS(
            "═══ Sincronização completa! ═══"
        ))
