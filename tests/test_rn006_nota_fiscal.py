from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_06_nota_fiscal import filtrar_nota_fiscal


def test_rn006_nota_fiscal_por_despesa_e_limite_exato():
    despesas = [
        Despesa(
            id="d-100",
            data=date(2026, 7, 6),
            categoria="transporte_urbano",
            fornecedor="Taxi A",
            valor=Decimal("100.00"),
            tem_nota_fiscal=False,
            indice_original=0,
        ),
        Despesa(
            id="d-101",
            data=date(2026, 7, 6),
            categoria="transporte_urbano",
            fornecedor="Taxi B",
            valor=Decimal("100.01"),
            tem_nota_fiscal=False,
            indice_original=1,
        ),
        Despesa(
            id="d-nota",
            data=date(2026, 7, 6),
            categoria="transporte_urbano",
            fornecedor="Taxi C",
            valor=Decimal("101.00"),
            tem_nota_fiscal=True,
            indice_original=2,
        ),
    ]

    despesas_pendentes, resultados_recusados = filtrar_nota_fiscal(despesas)

    assert [despesa.id for despesa in despesas_pendentes] == ["d-100", "d-nota"]
    assert len(resultados_recusados) == 1
    resultado = resultados_recusados[0]
    assert resultado.id == "d-101"
    assert resultado.valor_reembolsavel == Decimal("0.00")
    assert resultado.status == "RECUSADO"
    assert resultado.motivo == "NF_AUSENTE"
