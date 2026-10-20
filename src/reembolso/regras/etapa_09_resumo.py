"""Etapa de consolidação do resumo da execução."""

from decimal import Decimal

from reembolso.modelos import ResultadoDespesa, ResumoExecucao, StatusDespesa


_STATUS: tuple[StatusDespesa, ...] = (
    "APROVADO",
    "PARCIAL",
    "RECUSADO",
    "ESTORNO",
)


def calcular_resumo(resultados: list[ResultadoDespesa]) -> ResumoExecucao:
    total_solicitado = Decimal("0.00")
    total_reembolsavel = Decimal("0.00")
    contagem_por_status = {status: 0 for status in _STATUS}

    for resultado in resultados:
        contagem_por_status[resultado.status] += 1
        if resultado.status == "ESTORNO":
            continue
        total_solicitado += resultado.valor_solicitado
        total_reembolsavel += resultado.valor_reembolsavel

    return ResumoExecucao(
        total_solicitado=total_solicitado,
        total_reembolsavel=total_reembolsavel,
        total_recusado=total_solicitado - total_reembolsavel,
        contagem_por_status=contagem_por_status,
    )
