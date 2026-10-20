from decimal import Decimal

from reembolso.modelos import ResultadoDespesa
from reembolso.regras.etapa_09_resumo import calcular_resumo


def test_rn009_calcula_totais_e_contagem_por_status():
    resultados = [
        ResultadoDespesa(
            id="d-aprovada",
            valor_solicitado=Decimal("10.00"),
            valor_reembolsavel=Decimal("10.00"),
            status="APROVADO",
            motivo="",
        ),
        ResultadoDespesa(
            id="d-parcial",
            valor_solicitado=Decimal("20.00"),
            valor_reembolsavel=Decimal("15.00"),
            status="PARCIAL",
            motivo="LIMITE_EXCEDIDO",
        ),
        ResultadoDespesa(
            id="d-duplicada",
            valor_solicitado=Decimal("30.00"),
            valor_reembolsavel=Decimal("0.00"),
            status="RECUSADO",
            motivo="DUPLICADA",
            despesa_mantida="d-aprovada",
        ),
        ResultadoDespesa(
            id="d-estorno",
            valor_solicitado=Decimal("-45.00"),
            valor_reembolsavel=Decimal("0.00"),
            status="ESTORNO",
            motivo="ESTORNO",
        ),
    ]

    resumo = calcular_resumo(resultados)

    assert resumo.total_solicitado == Decimal("60.00")
    assert resumo.total_reembolsavel == Decimal("25.00")
    assert resumo.total_recusado == Decimal("35.00")
    assert resumo.contagem_por_status == {
        "APROVADO": 1,
        "PARCIAL": 1,
        "RECUSADO": 1,
        "ESTORNO": 1,
    }
    assert isinstance(resumo.total_solicitado, Decimal)
    assert isinstance(resumo.total_reembolsavel, Decimal)
    assert isinstance(resumo.total_recusado, Decimal)


def test_rn009_totais_e_contagem_do_caso_completo():
    resultados = [
        ResultadoDespesa(
            id=f"d-aprovada-{indice}",
            valor_solicitado=valor,
            valor_reembolsavel=valor,
            status="APROVADO",
            motivo="",
        )
        for indice, valor in enumerate(
            map(Decimal, ("100.00", "100.00", "100.00", "275.43"))
        )
    ]
    resultados.extend(
        ResultadoDespesa(
            id=f"d-parcial-{indice}",
            valor_solicitado=Decimal("100.00"),
            valor_reembolsavel=Decimal("80.00"),
            status="PARCIAL",
            motivo="LIMITE_EXCEDIDO",
        )
        for indice in range(3)
    )
    resultados.extend(
        ResultadoDespesa(
            id=f"d-recusada-{indice}",
            valor_solicitado=valor,
            valor_reembolsavel=Decimal("0.00"),
            status="RECUSADO",
            motivo="DUPLICADA",
        )
        for indice, valor in enumerate(
            map(
                Decimal,
                ("200.00", "200.00", "200.00", "200.00", "100.00", "86.41"),
            )
        )
    )
    resultados.append(
        ResultadoDespesa(
            id="d-estorno",
            valor_solicitado=Decimal("-45.00"),
            valor_reembolsavel=Decimal("0.00"),
            status="ESTORNO",
            motivo="ESTORNO",
        )
    )

    resumo = calcular_resumo(resultados)

    assert resumo.total_solicitado == Decimal("1861.84")
    assert resumo.total_reembolsavel == Decimal("815.43")
    assert resumo.total_recusado == Decimal("1046.41")
    assert resumo.contagem_por_status == {
        "APROVADO": 4,
        "PARCIAL": 3,
        "RECUSADO": 6,
        "ESTORNO": 1,
    }
