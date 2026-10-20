from decimal import Decimal

import pytest

from reembolso.entrada_saida import ErroEntrada, converter_entrada


def _entrada():
    return {
        "colaborador": {
            "id": "c-001",
            "nome": "Colaborador",
            "centro_custo": "CC-001",
        },
        "periodo": {
            "competencia": "2026-07",
            "inicio": "2026-07-01",
            "fim": "2026-07-31",
        },
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-06",
                "categoria": "alimentacao",
                "descricao": "Almoco",
                "fornecedor": "Restaurante",
                "valor": 33.33,
                "tem_nota_fiscal": True,
            }
        ],
    }


def test_rn010_entrada_invalida_tipos_datas_e_periodo():
    casos_invalidos = []

    entrada = _entrada()
    entrada["colaborador"]["id"] = 42
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["periodo"]["inicio"] = "2026-02-30"
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["periodo"]["fim"] = "31/07/2026"
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["despesas"][0]["data"] = "ontem"
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["despesas"][0]["valor"] = "33.33"
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["despesas"][0]["valor"] = True
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["despesas"][0]["tem_nota_fiscal"] = 1
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["despesas"][0]["descricao"] = 7
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["periodo"]["inicio"] = "2026-08-01"
    casos_invalidos.append(entrada)

    entrada = _entrada()
    entrada["periodo"]["fim"] = "2026-06-30"
    casos_invalidos.append(entrada)

    for dados in casos_invalidos:
        with pytest.raises(ErroEntrada):
            converter_entrada(dados)

    entrada_valida = converter_entrada(_entrada())
    assert entrada_valida.despesas[0].valor == Decimal("33.33")
    assert entrada_valida.despesas[0].data.isoformat() == "2026-07-06"
