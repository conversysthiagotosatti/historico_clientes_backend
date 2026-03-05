from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Chamado, ChamadoMensagem, ChamadoHistorico, ChamadoApontamento, ChamadoTimer,
    Cidade, Empresa, ClienteHelpdesk, Departamento, Filial,
    UsuarioHelpdesk, ContratoHelpdesk, AnexoContrato, Atendente,
    AtividadeChamado, AnexoChamado,
    Categoria, Servico, PrioridadeHelpdesk, StatusChamadoConfig,
    TipoChamado, Area, GrupoSolucao, Impacto, TemaTemplate, TemplateChamado,
    ItemConfiguracao, CampoCustomizavelIC, ValorCampoIC,
    Fornecedor, CentroCusto,
    FAQ, AnexoFAQ,
    Ligacao, PesquisaSatisfacao, ContestacaoChamado, FechamentoAvaliacao,
    FormularioAprovacao, CampoFormulario, ConfiguracaoAnexo,
)

User = get_user_model()


# =============================================
# Helpers
# =============================================
class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']




# =============================================
# Cidade
# =============================================
class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = '__all__'


# =============================================
# Empresa
# =============================================
class EmpresaSerializer(serializers.ModelSerializer):
    cidade_detalhes = CidadeSerializer(source='cidade', read_only=True)

    class Meta:
        model = Empresa
        fields = '__all__'


# =============================================
# Cliente Helpdesk
# =============================================
class ClienteHelpdeskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteHelpdesk
        fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj', 'cpf',
            'email', 'telefone', 'ativo', 'pendencia_financeira',
            'codigo_integracao', 'criado_em', 'atualizado_em',
        ]


class ClienteHelpdeskSerializer(serializers.ModelSerializer):
    cidade_detalhes = CidadeSerializer(source='cidade', read_only=True)
    empresa_detalhes = EmpresaSerializer(source='empresa', read_only=True)

    class Meta:
        model = ClienteHelpdesk
        fields = '__all__'


# =============================================
# Departamento
# =============================================
class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


# =============================================
# Filial
# =============================================
class FilialSerializer(serializers.ModelSerializer):
    cidade_detalhes = CidadeSerializer(source='cidade', read_only=True)

    class Meta:
        model = Filial
        fields = '__all__'


# =============================================
# Usuário Helpdesk
# =============================================
class UsuarioHelpdeskSerializer(serializers.ModelSerializer):
    user_detalhes = UserSimpleSerializer(source='user', read_only=True)

    class Meta:
        model = UsuarioHelpdesk
        fields = '__all__'


# =============================================
# Contrato Helpdesk
# =============================================
class AnexoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexoContrato
        fields = '__all__'


class ContratoHelpdeskSerializer(serializers.ModelSerializer):
    anexos = AnexoContratoSerializer(many=True, read_only=True)

    class Meta:
        model = ContratoHelpdesk
        fields = '__all__'


# =============================================
# Atendente
# =============================================
class AtendenteSerializer(serializers.ModelSerializer):
    user_detalhes = UserSimpleSerializer(source='user', read_only=True)

    class Meta:
        model = Atendente
        fields = '__all__'


# =============================================
# Atividade de Chamado
# =============================================
class AtividadeChamadoSerializer(serializers.ModelSerializer):
    atendente_detalhes = AtendenteSerializer(source='atendente', read_only=True)

    class Meta:
        model = AtividadeChamado
        fields = '__all__'


# =============================================
# Anexo de Chamado
# =============================================
class AnexoChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexoChamado
        fields = '__all__'


# =============================================
# Catálogo
# =============================================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ServicoSerializer(serializers.ModelSerializer):
    categoria_detalhes = CategoriaSerializer(source='categoria', read_only=True)

    class Meta:
        model = Servico
        fields = '__all__'


class PrioridadeHelpdeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioridadeHelpdesk
        fields = '__all__'


class StatusChamadoConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusChamadoConfig
        fields = '__all__'


class TipoChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoChamado
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class GrupoSolucaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoSolucao
        fields = '__all__'


class ImpactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impacto
        fields = '__all__'


class TemaTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemaTemplate
        fields = '__all__'


class TemplateChamadoSerializer(serializers.ModelSerializer):
    categoria_detalhes = CategoriaSerializer(source='categoria', read_only=True)
    servico_detalhes = ServicoSerializer(source='servico', read_only=True)
    tipo_detalhes = TipoChamadoSerializer(source='tipo', read_only=True)

    class Meta:
        model = TemplateChamado
        fields = '__all__'


# =============================================
# Item de Configuração
# =============================================
class CampoCustomizavelICSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoCustomizavelIC
        fields = '__all__'


class ValorCampoICSerializer(serializers.ModelSerializer):
    campo_detalhes = CampoCustomizavelICSerializer(source='campo', read_only=True)

    class Meta:
        model = ValorCampoIC
        fields = '__all__'


class ItemConfiguracaoSerializer(serializers.ModelSerializer):
    valores_customizados = ValorCampoICSerializer(many=True, read_only=True)

    class Meta:
        model = ItemConfiguracao
        fields = '__all__'


# =============================================
# Fornecedor
# =============================================
class FornecedorSerializer(serializers.ModelSerializer):
    cidade_detalhes = CidadeSerializer(source='cidade', read_only=True)
    area_detalhes = AreaSerializer(source='area', read_only=True)

    class Meta:
        model = Fornecedor
        fields = '__all__'


# =============================================
# Centro de Custo
# =============================================
class CentroCustoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroCusto
        fields = '__all__'


# =============================================
# FAQ
# =============================================
class AnexoFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexoFAQ
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
    anexos = AnexoFAQSerializer(many=True, read_only=True)

    class Meta:
        model = FAQ
        fields = '__all__'


# =============================================
# Ligação
# =============================================
class LigacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ligacao
        fields = '__all__'


# =============================================
# Pesquisa de Satisfação
# =============================================
class PesquisaSatisfacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PesquisaSatisfacao
        fields = '__all__'


# =============================================
# Contestação
# =============================================
class ContestacaoChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestacaoChamado
        fields = '__all__'


# =============================================
# Fechamento com Avaliação
# =============================================
class FechamentoAvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FechamentoAvaliacao
        fields = '__all__'


# =============================================
# Formulário
# =============================================
class CampoFormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoFormulario
        fields = '__all__'


class FormularioAprovacaoSerializer(serializers.ModelSerializer):
    campos = CampoFormularioSerializer(many=True, read_only=True)

    class Meta:
        model = FormularioAprovacao
        fields = '__all__'


# =============================================
# Configuração de Anexo
# =============================================
class ConfiguracaoAnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoAnexo
        fields = '__all__'


# =============================================
# Chamado (expandido)
# =============================================
class ChamadoMensagemSerializer(serializers.ModelSerializer):
    autor_detalhes = UserSimpleSerializer(source='autor', read_only=True)

    class Meta:
        model = ChamadoMensagem
        fields = '__all__'


class ChamadoHistoricoSerializer(serializers.ModelSerializer):
    usuario_detalhes = UserSimpleSerializer(source='usuario', read_only=True)

    class Meta:
        model = ChamadoHistorico
        fields = '__all__'


class ChamadoApontamentoSerializer(serializers.ModelSerializer):
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)

    class Meta:
        model = ChamadoApontamento
        fields = '__all__'


class ChamadoTimerSerializer(serializers.ModelSerializer):
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)

    class Meta:
        model = ChamadoTimer
        fields = '__all__'


class ChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamado
        fields = "__all__"


class ChamadoListSerializer(serializers.ModelSerializer):
    grupo_solucao_detalhes = GrupoSolucaoSerializer(source='grupo_solucao', read_only=True)
    solicitante_detalhes = UserSimpleSerializer(source='solicitante', read_only=True)
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)
    categoria_detalhes = CategoriaSerializer(source='categoria', read_only=True)
    tipo_chamado_detalhes = TipoChamadoSerializer(source='tipo_chamado', read_only=True)
    cliente_helpdesk_detalhes = ClienteHelpdeskListSerializer(source='cliente_helpdesk', read_only=True)

    class Meta:
        model = Chamado
        fields = [
            'id', 'titulo', 'status', 'prioridade',
            'grupo_solucao', 'grupo_solucao_detalhes',
            'solicitante', 'solicitante_detalhes', 'atendente', 'atendente_detalhes',
            'categoria', 'categoria_detalhes',
            'tipo_chamado', 'tipo_chamado_detalhes',
            'cliente_helpdesk', 'cliente_helpdesk_detalhes',
            'criado_em', 'atualizado_em', 'resolvido_em', 'sla_horas',
            'codigo_integracao',
        ]


class ChamadoDetailSerializer(serializers.ModelSerializer):
    solicitante_detalhes = UserSimpleSerializer(source='solicitante', read_only=True)
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)
    categoria_detalhes = CategoriaSerializer(source='categoria', read_only=True)
    servico_detalhes = ServicoSerializer(source='servico', read_only=True)
    tipo_chamado_detalhes = TipoChamadoSerializer(source='tipo_chamado', read_only=True)
    area_detalhes = AreaSerializer(source='area', read_only=True)
    cliente_helpdesk_detalhes = ClienteHelpdeskListSerializer(source='cliente_helpdesk', read_only=True)
    impacto_detalhes = ImpactoSerializer(source='impacto', read_only=True)
    grupo_solucao_detalhes = GrupoSolucaoSerializer(source='grupo_solucao', read_only=True)
    atendente_helpdesk_detalhes = AtendenteSerializer(source='atendente_helpdesk', read_only=True)

    class Meta:
        model = Chamado
        fields = '__all__'
