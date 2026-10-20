import json

import pytest

from reembolso.cli import main


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


def test_rn010_codigos_de_saida(tmp_path, capsys):
    entrada = tmp_path / "entrada.json"
    saida = tmp_path / "saida.json"
    entrada.write_text(json.dumps(_entrada()), encoding="utf-8")

    assert main([str(entrada), str(saida)]) == 0
    saida_json = json.loads(saida.read_text(encoding="utf-8"))
    assert saida_json["itens"][0]["id"] == "d-001"
    assert saida_json["itens"][0]["valor_reembolsavel"] == 42.00
    assert capsys.readouterr().err == ""

    entrada_invalida = tmp_path / "entrada-invalida.json"
    dados_invalidos = _entrada()
    del dados_invalidos["despesas"][0]["valor"]
    entrada_invalida.write_text(json.dumps(dados_invalidos), encoding="utf-8")
    saida_invalida = tmp_path / "saida-invalida.json"

    assert main([str(entrada_invalida), str(saida_invalida)]) == 1
    assert "d-001" in capsys.readouterr().err
    assert not saida_invalida.exists()

    with pytest.raises(SystemExit) as erro_uso:
        main([])
    assert erro_uso.value.code == 2
