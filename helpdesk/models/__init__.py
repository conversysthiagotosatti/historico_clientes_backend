# helpdesk/models/__init__.py
# Re-exporta todos os modelos para manter compatibilidade de imports

from .base import Setor  # noqa: F401

from .chamado import (  # noqa: F401
    ChamadoStatus, ChamadoPrioridade, Chamado,
    ChamadoTipoAutor, ChamadoMensagem, ChamadoHistorico,
    ChamadoApontamento, ChamadoTimerEstado, ChamadoTimer,
)

from .cidade import Cidade  # noqa: F401
from .empresa import Empresa  # noqa: F401
from .cliente_hd import ClienteHelpdesk  # noqa: F401
from .departamento import Departamento  # noqa: F401
from .filial import Filial  # noqa: F401
from .usuario_hd import UsuarioHelpdesk  # noqa: F401
from .contrato_hd import ContratoHelpdesk, AnexoContrato  # noqa: F401
from .atendente import Atendente  # noqa: F401
from .atividade import AtividadeChamado  # noqa: F401
from .anexo import AnexoChamado  # noqa: F401

from .catalogo import (  # noqa: F401
    Categoria, Servico, PrioridadeHelpdesk, StatusChamadoConfig,
    TipoChamado, Area, GrupoSolucao, Impacto, TemaTemplate, TemplateChamado,
)

from .ic import ItemConfiguracao, CampoCustomizavelIC, ValorCampoIC  # noqa: F401
from .fornecedor import Fornecedor  # noqa: F401
from .centro_custo import CentroCusto  # noqa: F401
from .base_conhecimento import FAQ, AnexoFAQ  # noqa: F401
from .ligacao import Ligacao  # noqa: F401
from .satisfacao import PesquisaSatisfacao  # noqa: F401
from .contestacao import ContestacaoChamado  # noqa: F401
from .fechamento import FechamentoAvaliacao  # noqa: F401
from .formulario import FormularioAprovacao, CampoFormulario  # noqa: F401
from .config_anexo import ConfiguracaoAnexo  # noqa: F401
