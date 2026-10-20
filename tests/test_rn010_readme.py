from pathlib import Path


def test_rn010_comando_documentado_no_readme():
    raiz = Path(__file__).resolve().parents[1]
    conteudo = (raiz / "README.md").read_text(encoding="utf-8")

    assert "pytest -q" in conteudo
    assert "python -m reembolso" in conteudo
    assert "exemplos/despesas-exemplo.json" in conteudo
    assert "colaborador" in conteudo
    assert "periodo" in conteudo
    assert "despesas" in conteudo
    assert "itens" in conteudo
    assert "resumo" in conteudo
