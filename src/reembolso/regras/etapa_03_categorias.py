"""Etapa de validação das categorias."""

from decimal import Decimal

from reembolso.configuracao import CATEGORIAS_VALIDAS
from reembolso.modelos import Despesa, ResultadoDespesa


def filtrar_categorias(
    despesas: list[Despesa],
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_recusados = []

    for despesa in despesas:
        if despesa.categoria not in CATEGORIAS_VALIDAS:
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
