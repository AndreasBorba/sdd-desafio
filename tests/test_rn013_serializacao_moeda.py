import json
from decimal import Decimal
from pathlib import Path

from reembolso.cli import main


def test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    entrada = tmp_path / "despesas.json"
    saida = tmp_path / "resultado.json"
    entrada.write_text(
        """
        {
          "colaborador": {"id": "c-001", "centro_custo": "CC-COMERCIAL"},
          "periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"},
          "despesas": [
            {
              "id": "convertida", "data": "2026-07-14",
              "categoria": "alimentacao", "fornecedor": "Lisboa",
              "valor": 22, "moeda": "EUR", "tem_nota_fiscal": true
            },
            {
              "id": "sem-cambio", "data": "2026-07-21",
              "categoria": "representacao", "fornecedor": "Londres",
              "valor": 55, "moeda": "GBP", "tem_nota_fiscal": true
            },
            {
              "id": "estorno", "data": "2026-07-14",
              "categoria": "alimentacao", "fornecedor": "Lisboa",
              "valor": -2, "moeda": "EUR", "tem_nota_fiscal": false
            },
            {
              "id": "brl", "data": "2026-07-23",
              "categoria": "alimentacao", "fornecedor": "Brasil",
              "valor": 33.333, "tem_nota_fiscal": true
            }
          ]
        }
        """,
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
            str(raiz / "exemplos" / "envelope" / "politica-v4.json"),
            "--cambio",
            str(raiz / "exemplos" / "envelope" / "cambio.json"),
        ]
    ) == 0

    resultado = json.loads(
        saida.read_text(encoding="utf-8"),
        parse_float=Decimal,
    )
    itens = {item["id"]: item for item in resultado["itens"]}

    assert itens["convertida"]["valor_solicitado"] == Decimal("130.46")
    assert itens["convertida"]["valor_reembolsavel"] == Decimal("90.00")
    assert itens["convertida"]["moeda_original"] == "EUR"
    assert itens["convertida"]["valor_original"] == Decimal("22")
    assert itens["convertida"]["taxa_cambio"] == Decimal("5.93")
    assert itens["convertida"]["data_taxa_cambio"] == "2026-07-14"

    assert itens["sem-cambio"]["motivo"] == "CAMBIO_INDISPONIVEL"
    assert itens["sem-cambio"]["valor_solicitado"] == Decimal("0.00")
    assert itens["sem-cambio"]["moeda_original"] == "GBP"
    assert itens["sem-cambio"]["valor_original"] == Decimal("55")
    assert "taxa_cambio" not in itens["sem-cambio"]
    assert "data_taxa_cambio" not in itens["sem-cambio"]

    assert itens["estorno"]["status"] == "ESTORNO"
    assert itens["estorno"]["valor_solicitado"] == Decimal("0.00")
    assert itens["estorno"]["moeda_original"] == "EUR"
    assert itens["estorno"]["valor_original"] == Decimal("-2")
    assert "taxa_cambio" not in itens["estorno"]
    assert "data_taxa_cambio" not in itens["estorno"]

    assert itens["brl"]["valor_solicitado"] == Decimal("33.33")
    assert "moeda_original" not in itens["brl"]
    assert "valor_original" not in itens["brl"]
    assert "taxa_cambio" not in itens["brl"]
    assert "data_taxa_cambio" not in itens["brl"]
    assert resultado["resumo"]["total_solicitado"] == Decimal("163.79")
    assert resultado["resumo"]["total_reembolsavel"] == Decimal("123.33")
