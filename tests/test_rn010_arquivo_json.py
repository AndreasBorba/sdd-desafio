import pytest

from reembolso.entrada_saida import ErroEntrada, ler_entrada


def test_rn010_entrada_invalida_arquivo_e_json(tmp_path):
    caminho_saida = tmp_path / "saida.json"
    caminho_inexistente = tmp_path / "inexistente.json"

    with pytest.raises(ErroEntrada, match="não encontrado"):
        ler_entrada(caminho_inexistente)
    assert not caminho_saida.exists()

    caminho_json_invalido = tmp_path / "entrada-invalida.json"
    caminho_json_invalido.write_text('{"despesas": [}', encoding="utf-8")
    with pytest.raises(ErroEntrada, match="JSON"):
        ler_entrada(caminho_json_invalido)
    assert not caminho_saida.exists()
