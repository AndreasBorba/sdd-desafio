from decimal import Decimal
from pathlib import Path

from reembolso.entrada_saida import converter_entrada
from reembolso.pipeline import processar
from reembolso.politica import carregar_politica, resolver_regra_categoria


def test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero():
    raiz = Path(__file__).resolve().parents[1]
    politica = carregar_politica(
        raiz / "exemplos" / "envelope" / "politica-v4.json"
    )

    assert resolver_regra_categoria(
        politica,
        " cc-eng-plataforma ",
        "alimentacao",
    )["limite"] == Decimal("75.00")
    assert resolver_regra_categoria(
        politica,
        "CC-ADM",
        "hospedagem",
    )["limite"] == Decimal("250.00")
    assert resolver_regra_categoria(
        politica,
        "CC-NAO-CADASTRADO",
        "transporte_urbano",
    )["limite"] == Decimal("80.00")
    assert resolver_regra_categoria(
        politica,
        None,
        "coworking",
    ) is None

    entrada = converter_entrada(
        {
            "colaborador": {
                "id": "c-001",
                "centro_custo": " cc-eng-plataforma ",
            },
            "periodo": {
                "inicio": "2026-07-01",
                "fim": "2026-07-31",
            },
            "despesas": [
                {
                    "id": "d-hospedagem",
                    "data": "2026-07-10",
                    "categoria": "hospedagem",
                    "descricao": "Hotel - 1 diaria",
                    "fornecedor": "Hotel",
                    "valor": 100.00,
                    "tem_nota_fiscal": True,
                }
            ],
        }
    )
    resultado = processar(entrada, politica)

    assert resultado.resultados[0].status == "RECUSADO"
    assert resultado.resultados[0].motivo == "CATEGORIA_FORA_POLITICA"
    assert resultado.resultados[0].valor_reembolsavel == Decimal("0.00")
