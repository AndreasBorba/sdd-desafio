from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_01_normalizacao import normalizar_despesas


def test_rn001_arredonda_valor_e_normaliza_categoria():
    entrada = [
        Despesa(
            id="d-001",
            data=date(2026, 7, 3),
            categoria="  ALIMENTAÇÃO ",
            fornecedor="Restaurante",
            valor=Decimal("33.335"),
            tem_nota_fiscal=True,
            indice_original=0,
        ),
        Despesa(
            id="d-002",
            data=date(2026, 7, 3),
            categoria="Transporte_Urbano",
            fornecedor="Taxi",
            valor=Decimal("54.90"),
            tem_nota_fiscal=True,
            indice_original=1,
        ),
    ]

    resultado = normalizar_despesas(entrada)

    assert [(despesa.categoria, despesa.valor) for despesa in resultado] == [
        ("alimentacao", Decimal("33.34")),
        ("transporte_urbano", Decimal("54.90")),
    ]
    assert resultado[0].alertas == ["VALOR_ARREDONDADO"]
    assert resultado[1].alertas == []
    assert entrada[0].categoria == "  ALIMENTAÇÃO "
    assert entrada[0].valor == Decimal("33.335")
