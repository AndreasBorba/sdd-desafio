"""Etapa de aplicação dos tetos de reembolso."""

from datetime import date
from decimal import Decimal, ROUND_DOWN
from collections.abc import Mapping
from typing import Any

from reembolso.configuracao import (
    FATOR_AMPLIACAO_VIAGEM,
    TETOS_BASE,
    TETOS_EM_VIAGEM,
)
from reembolso.modelos import Despesa, ResultadoDespesa
from reembolso.politica import resolver_regra_categoria
from reembolso.regras.etapa_07_viagem import identificar_noites


_CENTAVO = Decimal("0.01")
_CATEGORIAS_COM_TETO_AMPLIADO = frozenset(
    {"alimentacao", "transporte_urbano"}
)


def aplicar_tetos(
    despesas: list[Despesa],
    dias_viagem: set[date],
    politica: Mapping[str, Any] | None = None,
    centro_custo: str | None = None,
) -> list[ResultadoDespesa]:
    consumos_diarios: dict[tuple[date, str], Decimal] = {}
    resultados_por_indice: dict[int, ResultadoDespesa] = {}

    for despesa in sorted(
        despesas,
        key=lambda item: (item.data, item.indice_original),
    ):
        categoria = despesa.categoria
        regra = (
            resolver_regra_categoria(politica, centro_custo, categoria)
            if politica is not None
            else None
        )
        if politica is None:
            teto_base = TETOS_BASE[categoria]
            periodicidade = (
                "diaria" if categoria == "hospedagem" else "dia"
            )
            percentual_viagem = (
                (FATOR_AMPLIACAO_VIAGEM - Decimal("1")) * Decimal("100")
            )
        else:
            if regra is None:
                raise ValueError(
                    f"A categoria {categoria} não foi resolvida na política."
                )
            teto_base = regra["limite"]
            periodicidade = regra["periodicidade"]
            percentual_viagem = politica.get(
                "acrescimo_em_viagem_percentual",
                Decimal("50"),
            )

        esta_em_viagem = despesa.data in dias_viagem
        alertas = list(despesa.alertas)

        aplica_ampliacao = (
            esta_em_viagem
            and categoria in _CATEGORIAS_COM_TETO_AMPLIADO
        )
        if periodicidade == "diaria":
            noites = identificar_noites(despesa.descricao)
            if noites is None:
                noites = 1
                if "DIARIAS_NAO_IDENTIFICADAS" not in alertas:
                    alertas.append("DIARIAS_NAO_IDENTIFICADAS")
            teto = teto_base * noites
            restante = teto
        else:
            if aplica_ampliacao:
                fator_viagem = (
                    Decimal("1")
                    + percentual_viagem / Decimal("100")
                )
                teto = teto_base * fator_viagem
            elif politica is None and esta_em_viagem:
                teto = TETOS_EM_VIAGEM[categoria]
            else:
                teto = teto_base
            chave_diaria = (despesa.data, categoria)
            restante = teto - consumos_diarios.get(
                chave_diaria,
                Decimal("0.00"),
            )

        restante = max(restante, Decimal("0.00")).quantize(
            _CENTAVO,
            rounding=ROUND_DOWN,
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

        if periodicidade == "dia":
            consumos_diarios[chave_diaria] = (
                consumos_diarios.get(chave_diaria, Decimal("0.00"))
                + valor_reembolsavel
            )
            if (
                aplica_ampliacao
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
