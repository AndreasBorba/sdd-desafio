"""Etapa de normalização das despesas."""

import unicodedata
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP

from reembolso.modelos import Despesa


_CENTAVO = Decimal("0.01")


def _normalizar_categoria(categoria: str) -> str:
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", categoria)
        if not unicodedata.combining(caractere)
    )
    return sem_acentos.strip().casefold()


def normalizar_despesas(despesas: list[Despesa]) -> list[Despesa]:
    normalizadas = []
    for despesa in despesas:
        valor_original = (
            despesa.valor
            if despesa.valor_original is None
            else despesa.valor_original
        )
        valor_ajustado = despesa.valor
        alertas = list(despesa.alertas)
        if despesa.moeda == "BRL":
            valor_ajustado = despesa.valor.quantize(
                _CENTAVO,
                rounding=ROUND_HALF_UP,
            )
            if (
                valor_ajustado != despesa.valor
                and "VALOR_ARREDONDADO" not in alertas
            ):
                alertas.append("VALOR_ARREDONDADO")
        normalizadas.append(
            replace(
                despesa,
                categoria=_normalizar_categoria(despesa.categoria),
                valor=valor_ajustado,
                valor_original=valor_original,
                alertas=alertas,
            )
        )
    return normalizadas
