from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_05_duplicatas import filtrar_duplicatas


def test_rn005_duplica_recusa_e_identifica_despesa_mantida():
    despesas = [
        Despesa(
            id="d-006",
            data=date(2026, 7, 9),
            categoria="alimentacao",
            fornecedor="Bistro Central",
            valor=Decimal("54.90"),
            tem_nota_fiscal=True,
            indice_original=0,
        ),
        Despesa(
            id="d-007",
            data=date(2026, 7, 9),
            categoria="alimentacao",
            fornecedor="Bistro Central",
            valor=Decimal("54.90"),
            tem_nota_fiscal=True,
            indice_original=1,
        ),
        Despesa(
            id="d-008",
            data=date(2026, 7, 9),
            categoria="alimentacao",
            fornecedor="Outro Bistro",
            valor=Decimal("54.90"),
            tem_nota_fiscal=True,
            indice_original=2,
        ),
    ]

    despesas_pendentes, resultados_recusados = filtrar_duplicatas(despesas)

    assert [despesa.id for despesa in despesas_pendentes] == ["d-006", "d-008"]
    assert len(resultados_recusados) == 1
    assert resultados_recusados[0].id == "d-007"
    assert resultados_recusados[0].valor_reembolsavel == Decimal("0.00")
    assert resultados_recusados[0].status == "RECUSADO"
    assert resultados_recusados[0].motivo == "DUPLICADA"
    assert resultados_recusados[0].despesa_mantida == "d-006"
