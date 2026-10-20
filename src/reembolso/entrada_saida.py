"""Leitura e escrita dos dados da aplicação."""

from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Any

from reembolso.modelos import (
    Colaborador,
    Despesa,
    EntradaExecucao,
    Periodo,
)


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


def _validar_texto(
    valor: Any,
    campo: str,
    id_despesa: Any = None,
) -> str:
    if not isinstance(valor, str):
        detalhe = f"O campo {campo} deve ser um texto."
        if id_despesa is not None:
            detalhe = f"Despesa {id_despesa}: {detalhe}"
        raise ErroEntrada(detalhe)
    return valor


def _converter_data(valor: Any, campo: str) -> date:
    texto = _validar_texto(valor, campo)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto) is None:
        raise ErroEntrada(f"O campo {campo} deve ser uma data no formato AAAA-MM-DD.")
    try:
        return date.fromisoformat(texto)
    except ValueError as erro:
        raise ErroEntrada(f"O campo {campo} contém uma data inválida.") from erro


def _converter_valor(valor: Any, campo: str, id_despesa: str) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise ErroEntrada(
            f"Despesa {id_despesa}: o campo {campo} deve ser numérico."
        )
    try:
        convertido = Decimal(str(valor))
    except InvalidOperation as erro:
        raise ErroEntrada(
            f"Despesa {id_despesa}: o campo {campo} deve ser numérico."
        ) from erro
    if not convertido.is_finite():
        raise ErroEntrada(
            f"Despesa {id_despesa}: o campo {campo} deve ser um número finito."
        )
    return convertido


def converter_entrada(dados: Any) -> EntradaExecucao:
    validar_campos_obrigatorios(dados)

    colaborador_dados = dados["colaborador"]
    colaborador = Colaborador(
        id=_validar_texto(colaborador_dados["id"], "colaborador.id"),
        nome=(
            _validar_texto(colaborador_dados["nome"], "colaborador.nome")
            if "nome" in colaborador_dados
            else None
        ),
        centro_custo=(
            _validar_texto(
                colaborador_dados["centro_custo"],
                "colaborador.centro_custo",
            )
            if "centro_custo" in colaborador_dados
            else None
        ),
    )

    periodo_dados = dados["periodo"]
    periodo = Periodo(
        inicio=_converter_data(periodo_dados["inicio"], "periodo.inicio"),
        fim=_converter_data(periodo_dados["fim"], "periodo.fim"),
        competencia=(
            _validar_texto(
                periodo_dados["competencia"],
                "periodo.competencia",
            )
            if "competencia" in periodo_dados
            else None
        ),
    )
    if periodo.inicio > periodo.fim:
        raise ErroEntrada(
            "O início do período não pode ser posterior ao fim."
        )

    despesas = []
    for indice, dados_despesa in enumerate(dados["despesas"]):
        identificador = _validar_texto(
            dados_despesa["id"],
            f"despesas[{indice}].id",
        )
        categoria = _validar_texto(
            dados_despesa["categoria"],
            f"despesas[{indice}].categoria",
            identificador,
        )
        fornecedor = _validar_texto(
            dados_despesa["fornecedor"],
            f"despesas[{indice}].fornecedor",
            identificador,
        )
        data_despesa = _converter_data(
            dados_despesa["data"],
            f"despesas[{indice}].data",
        )
        valor = _converter_valor(
            dados_despesa["valor"],
            f"despesas[{indice}].valor",
            identificador,
        )
        tem_nota_fiscal = dados_despesa["tem_nota_fiscal"]
        if not isinstance(tem_nota_fiscal, bool):
            raise ErroEntrada(
                f"Despesa {identificador}: o campo tem_nota_fiscal deve ser booleano."
            )
        descricao = (
            _validar_texto(
                dados_despesa["descricao"],
                f"despesas[{indice}].descricao",
                identificador,
            )
            if "descricao" in dados_despesa
            else None
        )
        moeda = "BRL"
        if "moeda" in dados_despesa:
            moeda = _validar_texto(
                dados_despesa["moeda"],
                f"despesas[{indice}].moeda",
                identificador,
            ).strip().upper()
            if re.fullmatch(r"[A-Z]{3}", moeda) is None:
                raise ErroEntrada(
                    f"Despesa {identificador}: o campo moeda deve conter "
                    "três letras ISO 4217."
                )
        despesas.append(
            Despesa(
                id=identificador,
                data=data_despesa,
                categoria=categoria,
                descricao=descricao,
                fornecedor=fornecedor,
                valor=valor,
                tem_nota_fiscal=tem_nota_fiscal,
                indice_original=indice,
                moeda=moeda,
                valor_original=valor,
            )
        )

    return EntradaExecucao(
        colaborador=colaborador,
        periodo=periodo,
        despesas=despesas,
    )


def ler_entrada(caminho: str | Path) -> EntradaExecucao:
    caminho_entrada = Path(caminho)
    try:
        conteudo = caminho_entrada.read_text(encoding="utf-8")
    except FileNotFoundError as erro:
        raise ErroEntrada(
            f"Arquivo de entrada não encontrado: {caminho_entrada}"
        ) from erro
    except UnicodeDecodeError as erro:
        raise ErroEntrada(
            f"O arquivo de entrada não contém texto UTF-8 válido: {caminho_entrada}"
        ) from erro

    try:
        dados = json.loads(
            conteudo,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except json.JSONDecodeError as erro:
        raise ErroEntrada(
            f"JSON inválido no arquivo de entrada: {erro.msg}."
        ) from erro

    return converter_entrada(dados)


def montar_saida(resultado: Any) -> dict[str, Any]:
    itens = []
    for item in resultado.resultados:
        dados_item = {
            "id": item.id,
            "valor_solicitado": item.valor_solicitado,
            "valor_reembolsavel": item.valor_reembolsavel,
            "status": item.status,
            "motivo": item.motivo,
        }
        if item.despesa_mantida is not None:
            dados_item["despesa_mantida"] = item.despesa_mantida
        dados_item["alertas"] = list(item.alertas)
        if item.moeda_original is not None:
            dados_item["moeda_original"] = item.moeda_original
            dados_item["valor_original"] = item.valor_original
            if (
                item.taxa_cambio is not None
                and item.data_taxa_cambio is not None
            ):
                dados_item["taxa_cambio"] = item.taxa_cambio
                dados_item["data_taxa_cambio"] = item.data_taxa_cambio.isoformat()
        itens.append(dados_item)

    resumo = resultado.resumo
    return {
        "itens": itens,
        "resumo": {
            "total_solicitado": resumo.total_solicitado,
            "total_reembolsavel": resumo.total_reembolsavel,
            "total_recusado": resumo.total_recusado,
            "contagem_por_status": dict(resumo.contagem_por_status),
        },
    }


def _serializar_json(valor: Any, nivel: int = 0) -> str:
    recuo = "  " * nivel
    recuo_interno = "  " * (nivel + 1)

    if valor is None:
        return "null"
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    if isinstance(valor, Decimal):
        if not valor.is_finite():
            raise ValueError("Não é possível serializar Decimal não finito como JSON.")
        return format(valor.quantize(Decimal("0.01")), "f")
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, list):
        if not valor:
            return "[]"
        elementos = [
            f"{recuo_interno}{_serializar_json(item, nivel + 1)}"
            for item in valor
        ]
        return "[\n" + ",\n".join(elementos) + f"\n{recuo}]"
    if isinstance(valor, dict):
        if not valor:
            return "{}"
        membros = []
        for chave, item in valor.items():
            if not isinstance(chave, str):
                raise TypeError("As chaves de objetos JSON devem ser textos.")
            chave_json = json.dumps(chave, ensure_ascii=False)
            membros.append(
                f"{recuo_interno}{chave_json}: "
                f"{_serializar_json(item, nivel + 1)}"
            )
        return "{\n" + ",\n".join(membros) + f"\n{recuo}}}"
    raise TypeError(f"Tipo não serializável como JSON: {type(valor).__name__}.")


def serializar_saida(resultado: Any) -> str:
    return _serializar_json(montar_saida(resultado)) + "\n"
