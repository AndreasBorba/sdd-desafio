import json
from decimal import Decimal
from pathlib import Path

from reembolso.entrada_saida import converter_entrada
from reembolso.pipeline import processar
from reembolso.politica import carregar_politica


def _politica(tmp_path):
    dados = {
        "padrao": {
            "alimentacao": {"limite": 60.00, "periodicidade": "dia"},
            "transporte_urbano": {
                "limite": 10.01,
                "periodicidade": "dia",
            },
            "hospedagem": {"limite": 100.00, "periodicidade": "diaria"},
            "representacao": {"limite": 40.00, "periodicidade": "dia"},
        }
    }
    caminho = tmp_path / "politica.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return carregar_politica(caminho)


def _despesa(id_, data, categoria, fornecedor, valor, descricao=None):
    dados = {
        "id": id_,
        "data": data,
        "categoria": categoria,
        "fornecedor": fornecedor,
        "valor": valor,
        "tem_nota_fiscal": True,
    }
    if descricao is not None:
        dados["descricao"] = descricao
    return dados


def _entrada(despesas):
    return converter_entrada(
        {
            "colaborador": {"id": "c-001"},
            "periodo": {
                "inicio": "2026-07-01",
                "fim": "2026-07-31",
            },
            "despesas": despesas,
        }
    )


def test_rn008_periodicidade_e_categoria_definidas_na_politica(tmp_path):
    politica = _politica(tmp_path)
    entrada = _entrada(
        [
            _despesa("alimentacao-1", "2026-07-03", "alimentacao", "A", 65.00),
            _despesa("alimentacao-2", "2026-07-03", "alimentacao", "B", 10.00),
            _despesa(
                "hotel-2-noites",
                "2026-07-05",
                "hospedagem",
                "Hotel A",
                250.00,
                "Hotel - 2 noites",
            ),
            _despesa(
                "hotel-1-noite",
                "2026-07-05",
                "hospedagem",
                "Hotel B",
                90.00,
                "Hotel - 1 noite",
            ),
            _despesa(
                "hotel-viagem",
                "2026-07-10",
                "hospedagem",
                "Hotel C",
                80.00,
                "Hotel - 1 noite",
            ),
            _despesa(
                "hotel-teto-fracionado",
                "2026-07-15",
                "hospedagem",
                "Hotel F",
                80.00,
                "Hotel - 1 noite",
            ),
            _despesa(
                "representacao",
                "2026-07-11",
                "representacao",
                "Restaurante D",
                50.00,
            ),
            _despesa(
                "alimentacao-viagem",
                "2026-07-11",
                "alimentacao",
                "Restaurante E",
                85.00,
            ),
            _despesa(
                "transporte-teto-fracionado",
                "2026-07-16",
                "transporte_urbano",
                "TaxiApp G",
                15.02,
            ),
        ]
    )

    itens = {item.id: item for item in processar(entrada, politica).resultados}

    assert itens["alimentacao-1"].valor_reembolsavel == Decimal("60.00")
    assert itens["alimentacao-2"].status == "RECUSADO"
    assert itens["hotel-2-noites"].valor_reembolsavel == Decimal("200.00")
    assert itens["hotel-1-noite"].valor_reembolsavel == Decimal("90.00")
    assert itens["representacao"].valor_reembolsavel == Decimal("40.00")
    assert itens["alimentacao-viagem"].valor_reembolsavel == Decimal("85.00")
    assert "VIAGEM_INFERIDA" in itens["alimentacao-viagem"].alertas
    assert (
        itens["transporte-teto-fracionado"].valor_reembolsavel
        == Decimal("15.01")
    )
