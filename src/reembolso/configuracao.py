"""Configuração da política de reembolso."""

from decimal import Decimal
from types import MappingProxyType


TETOS_BASE = MappingProxyType(
    {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
        "hospedagem": Decimal("250.00"),
    }
)

CATEGORIAS_VALIDAS = frozenset(TETOS_BASE)

FATOR_AMPLIACAO_VIAGEM = Decimal("1.50")
_CATEGORIAS_COM_TETO_AMPLIADO = frozenset(
    {"alimentacao", "transporte_urbano"}
)
TETOS_EM_VIAGEM = MappingProxyType(
    {
        categoria: (
            teto * FATOR_AMPLIACAO_VIAGEM
            if categoria in _CATEGORIAS_COM_TETO_AMPLIADO
            else teto
        )
        for categoria, teto in TETOS_BASE.items()
    }
)

LIMIAR_NOTA_FISCAL = Decimal("100.00")
