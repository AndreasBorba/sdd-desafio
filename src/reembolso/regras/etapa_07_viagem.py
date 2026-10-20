"""Etapa de identificação de despesas em viagem."""

import re
import unicodedata
from dataclasses import replace
from datetime import date, timedelta

from reembolso.modelos import Despesa


_TRECHO_DIARIAS = re.compile(r"(\d+)\s*(diaria|diarias|noite|noites)\b")


def _normalizar_texto(texto: str) -> str:
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texto.casefold())
        if not unicodedata.combining(caractere)
    )


def identificar_noites(descricao: str | None) -> int | None:
    if descricao is None:
        return None

    for correspondencia in _TRECHO_DIARIAS.finditer(_normalizar_texto(descricao)):
        noites = int(correspondencia.group(1))
        if noites > 0:
            return noites
    return None


def identificar_viagem(
    despesas: list[Despesa],
) -> tuple[set[date], list[Despesa]]:
    dias_viagem: set[date] = set()
    despesas_atualizadas = []

    for despesa in despesas:
        alertas = [
            alerta
            for alerta in despesa.alertas
            if alerta != "DIARIAS_NAO_IDENTIFICADAS"
        ]
        if despesa.categoria == "hospedagem":
            noites = identificar_noites(despesa.descricao)
            if noites is None:
                noites = 1
                alertas.append("DIARIAS_NAO_IDENTIFICADAS")
            dias_viagem.update(
                despesa.data + timedelta(days=deslocamento)
                for deslocamento in range(noites + 1)
            )
        despesas_atualizadas.append(replace(despesa, alertas=alertas))

    return dias_viagem, despesas_atualizadas
