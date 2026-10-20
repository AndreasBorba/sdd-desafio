from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_02_estornos import separar_estornos


def test_rn002_estorno_nao_altera_teto():
    despesas = [
        Despesa(
            id="d-estorno",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("-45.00"),
            tem_nota_fiscal=False,
            indice_original=0,
        ),
        Despesa(
            id="d-normal",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Cantina",
            valor=Decimal("38.00"),
            tem_nota_fiscal=True,
            indice_original=1,
        ),
        Despesa(
            id="d-zero",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Cafe",
            valor=Decimal("0.00"),
            tem_nota_fiscal=False,
            indice_original=2,
        ),
    ]

    despesas_pendentes, resultados_estorno = separar_estornos(despesas)

    assert [despesa.id for despesa in despesas_pendentes] == ["d-normal", "d-zero"]
    assert len(resultados_estorno) == 1
    assert resultados_estorno[0].id == "d-estorno"
    assert resultados_estorno[0].valor_solicitado == Decimal("-45.00")
    assert resultados_estorno[0].valor_reembolsavel == Decimal("0.00")
    assert resultados_estorno[0].status == "ESTORNO"
    assert resultados_estorno[0].motivo == "ESTORNO"
