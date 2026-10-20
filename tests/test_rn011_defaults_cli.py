import json
from pathlib import Path

from reembolso.cli import main


def test_rn011_opcoes_politica_cambio_e_padroes(tmp_path, monkeypatch, capsys):
    raiz_projeto = Path(__file__).resolve().parents[1]
    entrada = raiz_projeto / "exemplos" / "despesas-exemplo.json"
    politica_padrao = (
        raiz_projeto / "exemplos" / "envelope" / "politica-v4.json"
    )
    cambio_padrao = raiz_projeto / "exemplos" / "envelope" / "cambio.json"
    assert politica_padrao.is_file()
    assert cambio_padrao.is_file()

    monkeypatch.chdir(tmp_path)
    saida_padrao = tmp_path / "saida-padrao.json"
    assert main(
        [
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida_padrao),
        ]
    ) == 0
    assert json.loads(saida_padrao.read_text(encoding="utf-8"))["itens"]

    saida_explicita = tmp_path / "saida-explicita.json"
    assert main(
        [
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida_explicita),
            "--politica",
            str(politica_padrao),
            "--cambio",
            str(cambio_padrao),
        ]
    ) == 0
    assert saida_explicita.is_file()

    saida_invalida = tmp_path / "saida-invalida.json"
    assert main(
        [
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida_invalida),
            "--politica",
            str(tmp_path / "ausente.json"),
        ]
    ) == 1
    assert "política" in capsys.readouterr().err
    assert not saida_invalida.exists()

    cambio_invalido = tmp_path / "cambio-invalido.json"
    cambio_invalido.write_text('{"taxas": [}', encoding="utf-8")
    assert main(
        [
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida_invalida),
            "--cambio",
            str(cambio_invalido),
        ]
    ) == 1
    assert "JSON inválido" in capsys.readouterr().err
    assert not saida_invalida.exists()
