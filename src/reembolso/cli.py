"""Fronteira de linha de comando da aplicação."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reembolso.entrada_saida import ErroEntrada, ler_entrada, serializar_saida
from reembolso.pipeline import processar


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calcula o reembolso de despesas de um arquivo JSON."
    )
    parser.add_argument("entrada", help="caminho do JSON de despesas")
    parser.add_argument("saida", help="caminho do JSON de resultado")
    argumentos = parser.parse_args(argv)

    try:
        entrada = ler_entrada(argumentos.entrada)
    except ErroEntrada as erro:
        print(str(erro), file=sys.stderr)
        return 1

    resultado = processar(entrada)
    conteudo = serializar_saida(resultado)
    try:
        Path(argumentos.saida).write_text(conteudo, encoding="utf-8")
    except OSError as erro:
        print(f"Não foi possível escrever o arquivo de saída: {erro}", file=sys.stderr)
        return 1
    return 0
