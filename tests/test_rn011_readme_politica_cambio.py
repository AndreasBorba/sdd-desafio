from pathlib import Path


def test_rn011_readme_documenta_politica_cambio_e_moeda():
    raiz = Path(__file__).resolve().parents[1]
    conteudo = (raiz / "README.md").read_text(encoding="utf-8").lower()

    assert "--politica" in conteudo
    assert "--cambio" in conteudo
    assert "politica-v4.json" in conteudo
    assert "cambio.json" in conteudo
    assert "moeda" in conteudo
    assert "brl" in conteudo
    assert "moeda_original" in conteudo
    assert "valor_original" in conteudo
    assert "taxa_cambio" in conteudo
    assert "data_taxa_cambio" in conteudo
    assert "cambio_indisponivel" in conteudo
    assert "5 dias" in conteudo
    assert "estorno" in conteudo
    assert "totais" in conteudo
