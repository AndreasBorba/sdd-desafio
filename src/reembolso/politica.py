"""Leitura e validação da política externa de reembolso."""

from collections.abc import Mapping
from decimal import Decimal
import json
from pathlib import Path
from typing import Any


class ErroPolitica(Exception):
    """Indica que o arquivo de política não atende ao contrato."""


_PERIODICIDADES_VALIDAS = frozenset({"dia", "diaria"})


def _validar_categorias(categorias: Any, caminho: str) -> None:
    if not isinstance(categorias, Mapping):
        raise ErroPolitica(f"A estrutura {caminho} deve ser um objeto.")

    for categoria, regra in categorias.items():
        if not isinstance(regra, Mapping):
            raise ErroPolitica(
                f"A configuração da categoria {categoria} em {caminho} "
                "deve ser um objeto."
            )

        limite = regra.get("limite")
        if (
            isinstance(limite, bool)
            or not isinstance(limite, Decimal)
            or not limite.is_finite()
            or limite < Decimal("0")
        ):
            raise ErroPolitica(
                f"O limite da categoria {categoria} em {caminho} "
                "deve ser um número não negativo."
            )

        periodicidade = regra.get("periodicidade")
        if periodicidade not in _PERIODICIDADES_VALIDAS:
            raise ErroPolitica(
                f"A periodicidade da categoria {categoria} em {caminho} "
                "é desconhecida."
            )


def carregar_politica(caminho: str | Path) -> dict[str, Any]:
    """Lê política JSON, convertendo todos os números para Decimal."""
    arquivo = Path(caminho)
    try:
        conteudo = arquivo.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError) as erro:
        raise ErroPolitica(
            f"Não foi possível ler o arquivo de política: {arquivo}"
        ) from erro

    try:
        dados = json.loads(
            conteudo,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except json.JSONDecodeError as erro:
        raise ErroPolitica(f"JSON inválido no arquivo de política: {erro.msg}.") from erro

    if not isinstance(dados, Mapping):
        raise ErroPolitica("A política deve ser um objeto JSON.")
    if "padrao" not in dados:
        raise ErroPolitica('A política deve conter a entrada "padrao".')

    _validar_categorias(dados["padrao"], "padrao")

    centros_custo = dados.get("centros_custo", {})
    if not isinstance(centros_custo, Mapping):
        raise ErroPolitica("A estrutura centros_custo deve ser um objeto.")
    for centro_custo, categorias in centros_custo.items():
        _validar_categorias(categorias, f"centros_custo.{centro_custo}")

    return dict(dados)
