import json
from decimal import Decimal

import pytest

from reembolso.politica import ErroPolitica, carregar_politica


def _politica():
    return {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "moeda_base": "BRL",
        "padrao": {
            "alimentacao": {"limite": 60.00, "periodicidade": "dia"},
            "hospedagem": {"limite": 250.00, "periodicidade": "diaria"},
        },
        "centros_custo": {
            "CC-001": {
                "alimentacao": {"limite": 75.00, "periodicidade": "dia"}
            }
        },
        "nota_fiscal_obrigatoria_acima_de": 100.00,
        "acrescimo_em_viagem_percentual": 50,
    }


def test_rn012_carrega_politica_externa_com_validacao_decimal(tmp_path):
    caminho = tmp_path / "politica.json"
    caminho.write_text(json.dumps(_politica()), encoding="utf-8")

    politica = carregar_politica(caminho)

    assert politica["padrao"]["alimentacao"]["limite"] == Decimal("60.00")
    assert isinstance(politica["padrao"]["alimentacao"]["limite"], Decimal)

    invalidas = []
    dados = _politica()
    del dados["padrao"]
    invalidas.append(dados)

    dados = _politica()
    dados["padrao"]["alimentacao"]["limite"] = -1
    invalidas.append(dados)

    dados = _politica()
    dados["padrao"]["alimentacao"]["periodicidade"] = "mensal"
    invalidas.append(dados)

    dados = _politica()
    dados["padrao"]["alimentacao"]["limite"] = "60.00"
    invalidas.append(dados)

    for indice, dados_invalidos in enumerate(invalidas):
        arquivo_invalido = tmp_path / f"politica-invalida-{indice}.json"
        arquivo_invalido.write_text(
            json.dumps(dados_invalidos),
            encoding="utf-8",
        )
        with pytest.raises(ErroPolitica):
            carregar_politica(arquivo_invalido)

    arquivo_json_invalido = tmp_path / "json-invalido.json"
    arquivo_json_invalido.write_text('{"padrao": [}', encoding="utf-8")
    with pytest.raises(ErroPolitica):
        carregar_politica(arquivo_json_invalido)
