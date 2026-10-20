"""Etapa de validação das categorias."""

from decimal import Decimal
from collections.abc import Mapping
from typing import Any

from reembolso.configuracao import CATEGORIAS_VALIDAS
from reembolso.modelos import Despesa, ResultadoDespesa
from reembolso.politica import resolver_regra_categoria


def filtrar_categorias(
    despesas: list[Despesa],
    politica: Mapping[str, Any] | None = None,
    centro_custo: str | None = None,
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_recusados = []

    for despesa in despesas:
        regra = (
            resolver_regra_categoria(
                politica,
                centro_custo,
                despesa.categoria,
            )
            if politica is not None
            else None
        )
        categoria_nao_reembolsavel = (
            regra["limite"] == Decimal("0")
            if regra is not None
            else False
        )
        categoria_desconhecida = (
            regra is None
            if politica is not None
            else despesa.categoria not in CATEGORIAS_VALIDAS
        )
        if categoria_desconhecida or categoria_nao_reembolsavel:
            resultados_recusados.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=despesa.valor,
                    valor_reembolsavel=Decimal("0.00"),
                    status="RECUSADO",
                    motivo="CATEGORIA_FORA_POLITICA",
                    alertas=list(despesa.alertas),
                )
            )
        else:
            despesas_pendentes.append(despesa)

    return despesas_pendentes, resultados_recusados
