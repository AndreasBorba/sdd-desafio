"""Fronteira de linha de comando da aplicação."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reembolso.entrada_saida import ErroEntrada, ler_entrada, serializar_saida
from reembolso.pipeline import processar


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
    argumentos = parser.parse_args(argv)

    try:
        entrada = ler_entrada(argumentos.caminho_entrada)
    except ErroEntrada as erro:
        print(str(erro), file=sys.stderr)
        return 1

    resultado = processar(entrada)
    conteudo = serializar_saida(resultado)
    try:
        Path(argumentos.caminho_saida).write_text(conteudo, encoding="utf-8")
    except OSError as erro:
        print(f"Não foi possível escrever o arquivo de saída: {erro}", file=sys.stderr)
        return 1
    return 0
