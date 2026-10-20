import json
from decimal import Decimal
from pathlib import Path

from reembolso.cli import main


def _despesa(
    identificador,
    data,
    categoria,
    valor,
    moeda=None,
    tem_nota_fiscal=True,
):
    despesa = {
        "id": identificador,
        "data": data,
        "categoria": categoria,
        "fornecedor": identificador,
        "valor": valor,
        "tem_nota_fiscal": tem_nota_fiscal,
    }
    if moeda is not None:
        despesa["moeda"] = moeda
    return despesa


def test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    politica = raiz / "exemplos" / "envelope" / "politica-v4.json"
    cambio = raiz / "exemplos" / "envelope" / "cambio.json"
    entrada = tmp_path / "despesas.json"
    saida = tmp_path / "resultado.json"
    entrada.write_text(
        json.dumps(
            {
                "colaborador": {
                    "id": "c-001",
                    "centro_custo": "CC-COMERCIAL",
                },
                "periodo": {
                    "inicio": "2026-07-01",
                    "fim": "2026-07-31",
                },
                "despesas": [
                    _despesa("eur-exato", "2026-07-14", "alimentacao", 22, " eur "),
                    _despesa("eur-exato-2", "2026-07-15", "alimentacao", 14.5, "EUR"),
                    _despesa("eur-sabado", "2026-07-18", "alimentacao", 30, "EUR"),
                    _despesa("usd-sem-nota", "2026-07-20", "transporte_urbano", 40, "USD", False),
                    _despesa("gbp-indisponivel", "2026-07-21", "representacao", 55, "GBP"),
                    _despesa("usd-janela", "2026-07-22", "alimentacao", 0.01, "USD"),
                    _despesa("usd-fora-janela", "2026-07-10", "alimentacao", 10, "USD"),
                    _despesa("brl", "2026-07-23", "alimentacao", 33.333),
                    _despesa("estorno-eur", "2026-07-14", "alimentacao", -2, "EUR"),
                ],
            }
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida),
            "--politica",
            str(politica),
            "--cambio",
            str(cambio),
        ]
    ) == 0
    itens = json.loads(
        saida.read_text(encoding="utf-8"),
        parse_float=Decimal,
    )["itens"]
    por_id = {item["id"]: item for item in itens}

    assert por_id["eur-exato"]["valor_solicitado"] == Decimal("130.46")
    assert por_id["eur-exato"]["valor_reembolsavel"] == Decimal("90.00")
    assert por_id["eur-exato-2"]["valor_solicitado"] == Decimal("85.26")
    assert por_id["eur-sabado"]["valor_solicitado"] == Decimal("178.80")
    assert por_id["eur-sabado"]["valor_reembolsavel"] == Decimal("90.00")
    assert por_id["usd-sem-nota"]["valor_solicitado"] == Decimal("220.00")
    assert por_id["usd-sem-nota"]["motivo"] == "NF_AUSENTE"
    assert por_id["gbp-indisponivel"]["valor_solicitado"] == Decimal("0.00")
    assert por_id["gbp-indisponivel"]["motivo"] == "CAMBIO_INDISPONIVEL"
    assert por_id["usd-janela"]["valor_solicitado"] == Decimal("0.05")
    assert "VALOR_ARREDONDADO" in por_id["usd-janela"]["alertas"]
    assert por_id["usd-fora-janela"]["motivo"] == "CAMBIO_INDISPONIVEL"
    assert por_id["brl"]["valor_solicitado"] == Decimal("33.33")
    assert "VALOR_ARREDONDADO" in por_id["brl"]["alertas"]
    assert por_id["estorno-eur"]["status"] == "ESTORNO"
    assert por_id["estorno-eur"]["valor_solicitado"] == Decimal("0.00")

    entrada_invalida = tmp_path / "moeda-invalida.json"
    dados_invalidos = json.loads(entrada.read_text(encoding="utf-8"))
    dados_invalidos["despesas"][0]["moeda"] = "EU"
    entrada_invalida.write_text(
        json.dumps(dados_invalidos),
        encoding="utf-8",
    )
    saida_invalida = tmp_path / "sem-saida.json"
    assert main(
        [
            "calcular",
            "--input",
            str(entrada_invalida),
            "--output",
            str(saida_invalida),
            "--politica",
            str(politica),
            "--cambio",
            str(cambio),
        ]
    ) == 1
    assert not saida_invalida.exists()
