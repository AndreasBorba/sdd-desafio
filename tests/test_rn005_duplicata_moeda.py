from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_05_duplicatas import filtrar_duplicatas


def _despesa(identificador, moeda, valor, valor_original, indice):
    return Despesa(
        id=identificador,
        data=date(2026, 7, 14),
        categoria="alimentacao",
        fornecedor="Restaurante",
        valor=Decimal(valor),
        tem_nota_fiscal=True,
        indice_original=indice,
        moeda=moeda,
        valor_original=Decimal(valor_original),
    )


def test_rn005_duplicata_exige_mesma_moeda_e_valor_original():
    despesas = [
        _despesa("eur-1", "EUR", "130.46", "22.00", 0),
        _despesa("eur-duplicada", "EUR", "130.46", "22.00", 1),
        _despesa("usd-mesmo-convertido", "USD", "130.46", "22.00", 2),
        _despesa("eur-outro-original", "EUR", "130.46", "21.99", 3),
    ]

    pendentes, recusadas = filtrar_duplicatas(despesas)

    assert [despesa.id for despesa in pendentes] == [
        "eur-1",
        "usd-mesmo-convertido",
        "eur-outro-original",
    ]
    assert [resultado.id for resultado in recusadas] == ["eur-duplicada"]
    assert recusadas[0].despesa_mantida == "eur-1"
