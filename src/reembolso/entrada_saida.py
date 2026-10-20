"""Leitura e escrita dos dados da aplicação."""

from collections.abc import Mapping
from typing import Any


class ErroEntrada(Exception):
    """Indica que a entrada não atende ao contrato da aplicação."""


def _exigir_campos(
    dados: Any,
    campos: tuple[str, ...],
    caminho: str,
    id_despesa: Any = None,
) -> Mapping[str, Any]:
    if not isinstance(dados, Mapping):
        detalhe = f"A estrutura {caminho} deve ser um objeto."
        if id_despesa is not None:
            detalhe = f"Despesa {id_despesa}: {detalhe}"
        raise ErroEntrada(detalhe)

    for campo in campos:
        if campo not in dados:
            detalhe = f"Campo obrigatório ausente: {caminho}.{campo}."
            if id_despesa is not None:
                detalhe = f"Despesa {id_despesa}: {detalhe}"
            raise ErroEntrada(detalhe)
    return dados


def validar_campos_obrigatorios(dados: Any) -> None:
    raiz = _exigir_campos(
        dados,
        ("colaborador", "periodo", "despesas"),
        "entrada",
    )
    _exigir_campos(
        raiz["colaborador"],
        ("id",),
        "colaborador",
    )
    _exigir_campos(
        raiz["periodo"],
        ("inicio", "fim"),
        "periodo",
    )
    despesas = raiz["despesas"]
    if not isinstance(despesas, list):
        raise ErroEntrada("O campo despesas deve ser uma lista.")

    campos_despesa = (
        "id",
        "data",
        "categoria",
        "fornecedor",
        "valor",
        "tem_nota_fiscal",
    )
    for indice, dados_despesa in enumerate(despesas):
        identificador = (
            dados_despesa.get("id")
            if isinstance(dados_despesa, Mapping)
            else None
        )
        _exigir_campos(
            dados_despesa,
            campos_despesa,
            f"despesas[{indice}]",
            identificador,
        )
