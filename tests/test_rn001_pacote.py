import importlib
from pathlib import Path


def test_rn001_pacote_base_e_importavel():
    modulos = (
        "reembolso",
        "reembolso.cli",
        "reembolso.entrada_saida",
        "reembolso.pipeline",
        "reembolso.regras",
    )

    for nome in modulos:
        modulo = importlib.import_module(nome)
        assert Path(modulo.__file__).is_file()
