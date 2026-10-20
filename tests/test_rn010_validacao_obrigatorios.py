import pytest

from reembolso.entrada_saida import ErroEntrada, validar_campos_obrigatorios


def _entrada():
    return {
        "colaborador": {"id": "c-001"},
        "periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-06",
                "categoria": "alimentacao",
                "fornecedor": "Restaurante",
                "valor": 42.00,
                "tem_nota_fiscal": True,
            }
        ],
    }


def test_rn010_entrada_invalida_campo_obrigatorio():
    entrada = _entrada()
    del entrada["despesas"][0]["valor"]

    with pytest.raises(ErroEntrada) as erro:
        validar_campos_obrigatorios(entrada)

    assert "d-001" in str(erro.value)
    assert "valor" in str(erro.value).lower()
    assert "obrigatório" in str(erro.value).lower()


def test_rn010_entrada_invalida_campo_obrigatorio_raiz():
    entrada = _entrada()
    del entrada["colaborador"]["id"]

    with pytest.raises(ErroEntrada, match="colaborador.id"):
        validar_campos_obrigatorios(entrada)
