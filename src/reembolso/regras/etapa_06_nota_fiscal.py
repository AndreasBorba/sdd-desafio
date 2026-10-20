"""Etapa de validação da nota fiscal."""

from decimal import Decimal

from reembolso.configuracao import LIMIAR_NOTA_FISCAL
from reembolso.modelos import Despesa, ResultadoDespesa


def filtrar_nota_fiscal(
    despesas: list[Despesa],
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    despesas_pendentes = []
    resultados_recusados = []

    for despesa in despesas:
        if despesa.valor > LIMIAR_NOTA_FISCAL and not despesa.tem_nota_fiscal:
            resultados_recusados.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=despesa.valor,
                    valor_reembolsavel=Decimal("0.00"),
                    status="RECUSADO",
                    motivo="NF_AUSENTE",
                    alertas=list(despesa.alertas),
                )
            )
        else:
            despesas_pendentes.append(despesa)

    return despesas_pendentes, resultados_recusados
