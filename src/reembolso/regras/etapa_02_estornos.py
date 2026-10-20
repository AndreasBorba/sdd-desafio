"""Etapa de identificação de estornos."""

from decimal import Decimal

from reembolso.modelos import Despesa, ResultadoDespesa


def separar_estornos(
    despesas: list[Despesa],
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_estorno = []

    for despesa in despesas:
        if despesa.valor < Decimal("0"):
            resultados_estorno.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=despesa.valor,
                    valor_reembolsavel=Decimal("0.00"),
                    status="ESTORNO",
                    motivo="ESTORNO",
                    alertas=list(despesa.alertas),
                )
            )
        else:
            despesas_pendentes.append(despesa)

    return despesas_pendentes, resultados_estorno
