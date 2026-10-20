from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa, Periodo
from reembolso.regras.etapa_04_periodo import filtrar_por_periodo


def test_rn004_periodo_inclui_inicio_e_fim():
    despesas = [
        Despesa(
            id="d-antes",
            data=date(2026, 6, 30),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("20.00"),
            tem_nota_fiscal=True,
            indice_original=0,
        ),
        Despesa(
            id="d-inicio",
            data=date(2026, 7, 1),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("20.00"),
            tem_nota_fiscal=True,
            indice_original=1,
        ),
        Despesa(
            id="d-fim",
            data=date(2026, 7, 31),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("20.00"),
            tem_nota_fiscal=True,
            indice_original=2,
        ),
        Despesa(
            id="d-depois",
            data=date(2026, 8, 1),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("20.00"),
            tem_nota_fiscal=True,
            indice_original=3,
        ),
    ]
    periodo = Periodo(
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )

    despesas_pendentes, resultados_recusados = filtrar_por_periodo(
        despesas,
        periodo,
    )

    assert [despesa.id for despesa in despesas_pendentes] == ["d-inicio", "d-fim"]
    assert [resultado.id for resultado in resultados_recusados] == [
        "d-antes",
        "d-depois",
    ]
    assert all(resultado.status == "RECUSADO" for resultado in resultados_recusados)
    assert all(
        resultado.motivo == "FORA_COMPETENCIA"
        and resultado.valor_reembolsavel == Decimal("0.00")
        for resultado in resultados_recusados
    )
