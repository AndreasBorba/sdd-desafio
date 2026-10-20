"""Leitura e resolução das cotações de câmbio."""

from collections.abc import Mapping
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re

from reembolso.modelos import Despesa, ResultadoDespesa


class ErroCambio(Exception):
    """Indica que o arquivo de câmbio não atende ao contrato."""


TaxasCambio = dict[date, dict[str, Decimal]]


def carregar_cambio(caminho: str | Path) -> TaxasCambio:
    """Lê as cotações e converte todos os valores numéricos para Decimal."""
    arquivo = Path(caminho)
    try:
        conteudo = arquivo.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erro:
        raise ErroCambio(
            f"Não foi possível ler o arquivo de câmbio: {arquivo}"
        ) from erro

    try:
        dados = json.loads(
            conteudo,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except json.JSONDecodeError as erro:
        raise ErroCambio(f"JSON inválido no arquivo de câmbio: {erro.msg}.") from erro

    if not isinstance(dados, Mapping):
        raise ErroCambio("O arquivo de câmbio deve conter um objeto JSON.")
    taxas = dados.get("taxas")
    if not isinstance(taxas, Mapping):
        raise ErroCambio("O campo taxas do arquivo de câmbio deve ser um objeto.")

    taxas_por_data: TaxasCambio = {}
    for texto_data, cotacoes in taxas.items():
        if (
            not isinstance(texto_data, str)
            or re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto_data) is None
        ):
            raise ErroCambio("As datas de cotação devem usar o formato AAAA-MM-DD.")
        try:
            data_cotacao = date.fromisoformat(texto_data)
        except ValueError as erro:
            raise ErroCambio(
                f"A data de cotação {texto_data} é inválida."
            ) from erro
        if not isinstance(cotacoes, Mapping):
            raise ErroCambio(
                f"As cotações de {texto_data} devem formar um objeto."
            )

        taxas_por_data[data_cotacao] = {}
        for moeda, taxa in cotacoes.items():
            if (
                not isinstance(moeda, str)
                or re.fullmatch(r"[A-Za-z]{3}", moeda) is None
            ):
                raise ErroCambio("As moedas das cotações devem ter três letras.")
            if (
                isinstance(taxa, bool)
                or not isinstance(taxa, Decimal)
                or not taxa.is_finite()
                or taxa <= Decimal("0")
            ):
                raise ErroCambio(
                    f"A cotação de {moeda} em {texto_data} deve ser positiva."
                )
            taxas_por_data[data_cotacao][moeda.upper()] = taxa

    return taxas_por_data


def resolver_taxa(
    taxas: Mapping[date, Mapping[str, Decimal]],
    moeda: str,
    data_despesa: date,
) -> tuple[Decimal, date] | None:
    """Obtém a cotação da data ou a mais recente nos cinco dias anteriores."""
    primeira_data = data_despesa - timedelta(days=5)
    for data_cotacao in sorted(taxas, reverse=True):
        if primeira_data <= data_cotacao <= data_despesa:
            taxa = taxas[data_cotacao].get(moeda)
            if taxa is not None:
                return taxa, data_cotacao
    return None


def converter_moedas(
    despesas: list[Despesa],
    taxas: Mapping[date, Mapping[str, Decimal]],
) -> tuple[list[Despesa], list[ResultadoDespesa]]:
    """Converte despesas estrangeiras e separa as sem cotação aplicável."""
    convertidas = []
    recusadas = []
    centavo = Decimal("0.01")

    for despesa in despesas:
        if despesa.moeda == "BRL":
            convertidas.append(despesa)
            continue

        cotacao = resolver_taxa(taxas, despesa.moeda, despesa.data)
        if cotacao is None:
            recusadas.append(
                ResultadoDespesa(
                    id=despesa.id,
                    valor_solicitado=Decimal("0.00"),
                    valor_reembolsavel=Decimal("0.00"),
                    status="RECUSADO",
                    motivo="CAMBIO_INDISPONIVEL",
                    alertas=list(despesa.alertas),
                )
            )
            continue

        taxa, data_taxa = cotacao
        valor_original = (
            despesa.valor
            if despesa.valor_original is None
            else despesa.valor_original
        )
        valor_calculado = valor_original * taxa
        valor_convertido = valor_calculado.quantize(
            centavo,
            rounding=ROUND_HALF_UP,
        )
        alertas = list(despesa.alertas)
        if (
            valor_calculado != valor_convertido
            and "VALOR_ARREDONDADO" not in alertas
        ):
            alertas.append("VALOR_ARREDONDADO")
        convertidas.append(
            replace(
                despesa,
                valor=valor_convertido,
                valor_original=valor_original,
                taxa_cambio=taxa,
                data_taxa_cambio=data_taxa,
                alertas=alertas,
            )
        )

    return convertidas, recusadas
