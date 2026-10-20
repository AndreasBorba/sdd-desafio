from datetime import date
from decimal import Decimal

from reembolso.modelos import (
    Colaborador,
    Despesa,
    EntradaExecucao,
    Periodo,
    ResultadoDespesa,
    ResultadoExecucao,
    ResumoExecucao,
)


def test_rn001_modelos_preservam_valores_decimais_e_ordem():
    despesas = [
        Despesa(
            id="d-002",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Cantina",
            valor=Decimal("38.00"),
            tem_nota_fiscal=True,
            descricao="Jantar",
            indice_original=1,
        ),
        Despesa(
            id="d-001",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("72.50"),
            tem_nota_fiscal=True,
            descricao="Almoco",
            indice_original=0,
        ),
    ]
    entrada = EntradaExecucao(
        colaborador=Colaborador(id="c-001"),
        periodo=Periodo(
            inicio=date(2026, 7, 1),
            fim=date(2026, 7, 31),
            competencia="2026-07",
        ),
        despesas=despesas,
    )
    resultados = [
        ResultadoDespesa(
            id=despesa.id,
            valor_solicitado=despesa.valor,
            valor_reembolsavel=Decimal("0.00"),
            status="RECUSADO",
            motivo="LIMITE_EXCEDIDO",
        )
        for despesa in entrada.despesas
    ]
    resumo = ResumoExecucao(
        total_solicitado=Decimal("110.50"),
        total_reembolsavel=Decimal("0.00"),
        total_recusado=Decimal("110.50"),
        contagem_por_status={"RECUSADO": 2},
    )
    resultado_execucao = ResultadoExecucao(
        resultados=resultados,
        resumo=resumo,
    )

    assert [despesa.id for despesa in entrada.despesas] == ["d-002", "d-001"]
    assert [item.id for item in resultado_execucao.resultados] == ["d-002", "d-001"]
    assert [despesa.indice_original for despesa in entrada.despesas] == [1, 0]
    assert all(isinstance(despesa.valor, Decimal) for despesa in entrada.despesas)
    assert all(
        isinstance(item.valor_solicitado, Decimal)
        and isinstance(item.valor_reembolsavel, Decimal)
        for item in resultado_execucao.resultados
    )
    assert isinstance(resultado_execucao.resumo.total_solicitado, Decimal)
    assert isinstance(resultado_execucao.resumo.total_reembolsavel, Decimal)
    assert isinstance(resultado_execucao.resumo.total_recusado, Decimal)
