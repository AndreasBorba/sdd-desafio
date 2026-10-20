"""Etapa de identificação de despesas duplicadas."""

from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa, ResultadoDespesa


def filtrar_duplicatas(
    despesas: list[Despesa],
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_recusados = []
    primeiras_ocorrencias: dict[
        tuple[date, str, str, str, Decimal],
        str,
    ] = {}

    for despesa in despesas:
        valor_original = (
            despesa.valor
            if despesa.valor_original is None
            else despesa.valor_original
        )
        chave = (
            despesa.data,
            despesa.categoria,
            despesa.fornecedor,
            despesa.moeda,
            valor_original,
        )
        despesa_mantida = primeiras_ocorrencias.get(chave)
        if despesa_mantida is not None:
            resultados_recusados.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=despesa.valor,
                    valor_reembolsavel=Decimal("0.00"),
                    status="RECUSADO",
                    motivo="DUPLICADA",
                    alertas=list(despesa.alertas),
                    despesa_mantida=despesa_mantida,
                )
            )
        else:
            primeiras_ocorrencias[chave] = despesa.id
            despesas_pendentes.append(despesa)

    return despesas_pendentes, resultados_recusados
