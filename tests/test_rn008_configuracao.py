from decimal import Decimal

from reembolso.configuracao import (
    CATEGORIAS_VALIDAS,
    LIMIAR_NOTA_FISCAL,
    TETOS_BASE,
    TETOS_EM_VIAGEM,
)


def test_rn008_configuracao_define_tetos_da_politica():
    assert CATEGORIAS_VALIDAS == {
        "alimentacao",
        "transporte_urbano",
        "hospedagem",
    }
    assert TETOS_BASE == {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
        "hospedagem": Decimal("250.00"),
    }
    assert TETOS_EM_VIAGEM == {
        "alimentacao": Decimal("90.00"),
        "transporte_urbano": Decimal("120.00"),
        "hospedagem": Decimal("250.00"),
    }
    assert LIMIAR_NOTA_FISCAL == Decimal("100.00")
    assert all(isinstance(valor, Decimal) for valor in TETOS_BASE.values())
    assert all(isinstance(valor, Decimal) for valor in TETOS_EM_VIAGEM.values())
