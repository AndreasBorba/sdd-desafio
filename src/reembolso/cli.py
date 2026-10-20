"""Fronteira de linha de comando da aplicação."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reembolso.cambio import ErroCambio, carregar_cambio
from reembolso.entrada_saida import ErroEntrada, ler_entrada, serializar_saida
from reembolso.pipeline import processar
from reembolso.politica import ErroPolitica, carregar_politica


_DIRETORIO_EXEMPLOS = (
    Path(__file__).resolve().parents[2] / "exemplos" / "envelope"
)
_POLITICA_PADRAO = _DIRETORIO_EXEMPLOS / "politica-v4.json"
_CAMBIO_PADRAO = _DIRETORIO_EXEMPLOS / "cambio.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Motor de cálculo de reembolso de despesas."
    )
    subcomandos = parser.add_subparsers(dest="comando", required=True)
    calcular = subcomandos.add_parser(
        "calcular",
        help="calcula o reembolso das despesas",
    )
    calcular.add_argument(
        "--input",
        required=True,
        dest="caminho_entrada",
        help="caminho do JSON de despesas",
    )
    calcular.add_argument(
        "--output",
        required=True,
        dest="caminho_saida",
        help="caminho do JSON de resultado",
    )
    calcular.add_argument(
        "--politica",
        default=str(_POLITICA_PADRAO),
        dest="caminho_politica",
        help="caminho do JSON de política",
    )
    calcular.add_argument(
        "--cambio",
        default=str(_CAMBIO_PADRAO),
        dest="caminho_cambio",
        help="caminho do JSON de câmbio",
    )
    argumentos = parser.parse_args(argv)

    try:
        entrada = ler_entrada(argumentos.caminho_entrada)
        politica = carregar_politica(argumentos.caminho_politica)
        taxas_cambio = carregar_cambio(argumentos.caminho_cambio)
    except (ErroCambio, ErroEntrada, ErroPolitica) as erro:
        print(str(erro), file=sys.stderr)
        return 1

    resultado = processar(entrada, politica, taxas_cambio)
    conteudo = serializar_saida(resultado)
    try:
        Path(argumentos.caminho_saida).write_text(conteudo, encoding="utf-8")
    except OSError as erro:
        print(f"Não foi possível escrever o arquivo de saída: {erro}", file=sys.stderr)
        return 1
    return 0
