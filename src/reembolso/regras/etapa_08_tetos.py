"""Etapa de aplicação dos tetos de reembolso."""

from datetime import date
from decimal import Decimal

from reembolso.configuracao import TETOS_BASE, TETOS_EM_VIAGEM
from reembolso.modelos import Despesa, ResultadoDespesa
from reembolso.regras.etapa_07_viagem import identificar_noites


def aplicar_tetos(
    despesas: list[Despesa],
    dias_viagem: set[date],
) -> list[ResultadoDespesa]:
    consumos_diarios: dict[tuple[date, str], Decimal] = {}
    resultados_por_indice: dict[int, ResultadoDespesa] = {}

    for despesa in sorted(
        despesas,
        key=lambda item: (item.data, item.indice_original),
    ):
        categoria = despesa.categoria
        teto_base = TETOS_BASE[categoria]
        esta_em_viagem = despesa.data in dias_viagem
        alertas = list(despesa.alertas)

        if categoria == "hospedagem":
            noites = identificar_noites(despesa.descricao)
            if noites is None:
                noites = 1
                if "DIARIAS_NAO_IDENTIFICADAS" not in alertas:
                    alertas.append("DIARIAS_NAO_IDENTIFICADAS")
            teto = teto_base * noites
            restante = teto
        else:
            teto = (
                TETOS_EM_VIAGEM[categoria]
                if esta_em_viagem
                else teto_base
            )
            chave_diaria = (despesa.data, categoria)
            restante = teto - consumos_diarios.get(
                chave_diaria,
                Decimal("0.00"),
            )

        valor_reembolsavel = min(despesa.valor, restante)
        if valor_reembolsavel == despesa.valor:
            status = "APROVADO"
            motivo = ""
        elif valor_reembolsavel > Decimal("0.00"):
            status = "PARCIAL"
            motivo = "LIMITE_EXCEDIDO"
        else:
            status = "RECUSADO"
            motivo = "LIMITE_EXCEDIDO"

        if categoria != "hospedagem":
            consumos_diarios[chave_diaria] = (
                consumos_diarios.get(chave_diaria, Decimal("0.00"))
                + valor_reembolsavel
            )
            if (
                esta_em_viagem
                and valor_reembolsavel > teto_base
                and "VIAGEM_INFERIDA" not in alertas
            ):
                alertas.append("VIAGEM_INFERIDA")

        resultados_por_indice[despesa.indice_original] = ResultadoDespesa(
            id=despesa.id,
            valor_solicitado=despesa.valor,
            valor_reembolsavel=valor_reembolsavel,
            status=status,
            motivo=motivo,
            alertas=alertas,
        )

    return [
        resultados_por_indice[indice]
        for indice in sorted(resultados_por_indice)
    ]
