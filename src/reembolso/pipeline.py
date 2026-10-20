"""Coordenação do cálculo das despesas."""

from collections.abc import Mapping
from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Any

from reembolso.cambio import converter_moedas
from reembolso.configuracao import LIMIAR_NOTA_FISCAL
from reembolso.modelos import EntradaExecucao, ResultadoExecucao
from reembolso.regras.etapa_01_normalizacao import normalizar_despesas
from reembolso.regras.etapa_02_estornos import separar_estornos
from reembolso.regras.etapa_03_categorias import filtrar_categorias
from reembolso.regras.etapa_04_periodo import filtrar_por_periodo
from reembolso.regras.etapa_05_duplicatas import filtrar_duplicatas
from reembolso.regras.etapa_06_nota_fiscal import filtrar_nota_fiscal
from reembolso.regras.etapa_07_viagem import identificar_viagem
from reembolso.regras.etapa_08_tetos import aplicar_tetos
from reembolso.regras.etapa_09_resumo import calcular_resumo


def processar(
    entrada: EntradaExecucao,
    politica: Mapping[str, Any] | None = None,
    taxas_cambio: Mapping[date, Mapping[str, Decimal]] | None = None,
) -> ResultadoExecucao:
    despesas = normalizar_despesas(entrada.despesas)
    despesas_originais = {despesa.id: despesa for despesa in despesas}
    resultados = []

    despesas, estornos = separar_estornos(despesas)
    resultados.extend(estornos)

    despesas, recusadas = converter_moedas(despesas, taxas_cambio or {})
    resultados.extend(recusadas)
    despesas_convertidas = {despesa.id: despesa for despesa in despesas}

    despesas, recusadas = filtrar_categorias(
        despesas,
        politica,
        entrada.colaborador.centro_custo,
    )
    resultados.extend(recusadas)

    despesas, recusadas = filtrar_por_periodo(despesas, entrada.periodo)
    resultados.extend(recusadas)

    despesas, recusadas = filtrar_duplicatas(despesas)
    resultados.extend(recusadas)

    limiar_nota_fiscal = (
        politica.get("nota_fiscal_obrigatoria_acima_de", LIMIAR_NOTA_FISCAL)
        if politica is not None
        else LIMIAR_NOTA_FISCAL
    )
    despesas, recusadas = filtrar_nota_fiscal(
        despesas,
        limiar_nota_fiscal,
    )
    resultados.extend(recusadas)

    dias_viagem, despesas = identificar_viagem(despesas)
    resultados.extend(
        aplicar_tetos(
            despesas,
            dias_viagem,
            politica,
            entrada.colaborador.centro_custo,
        )
    )

    ordem_por_id = {
        despesa.id: despesa.indice_original
        for despesa in entrada.despesas
    }
    resultados_com_metadados = []
    for resultado in resultados:
        despesa_original = despesas_originais[resultado.id]
        if despesa_original.moeda == "BRL":
            resultados_com_metadados.append(resultado)
            continue

        despesa_convertida = despesas_convertidas.get(
            resultado.id,
            despesa_original,
        )
        resultados_com_metadados.append(
            replace(
                resultado,
                moeda_original=despesa_original.moeda,
                valor_original=despesa_original.valor_original,
                taxa_cambio=despesa_convertida.taxa_cambio,
                data_taxa_cambio=despesa_convertida.data_taxa_cambio,
            )
        )
    resultados = resultados_com_metadados
    resultados.sort(key=lambda resultado: ordem_por_id[resultado.id])

    return ResultadoExecucao(
        resultados=resultados,
        resumo=calcular_resumo(resultados),
    )
