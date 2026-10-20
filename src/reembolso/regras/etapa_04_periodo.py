"""Etapa de validação do período da competência."""

from decimal import Decimal

from reembolso.modelos import Despesa, Periodo, ResultadoDespesa


def filtrar_por_periodo(
    despesas: list[Despesa],
    periodo: Periodo,
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_recusados = []

    for despesa in despesas:
        if periodo.inicio <= despesa.data <= periodo.fim:
            despesas_pendentes.append(despesa)
        else:
            resultados_recusados.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=despesa.valor,
                    valor_reembolsavel=Decimal("0.00"),
                    status="RECUSADO",
                    motivo="FORA_COMPETENCIA",
                    alertas=list(despesa.alertas),
                )
            )

    return despesas_pendentes, resultados_recusados
