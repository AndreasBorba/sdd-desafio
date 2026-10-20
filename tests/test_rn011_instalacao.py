import json
import os
from pathlib import Path
import subprocess
import sys


def test_rn011_comando_executa_a_partir_da_raiz(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    entrada = raiz / "exemplos" / "despesas-exemplo.json"
    saida = tmp_path / "resultado.json"
    ambiente = os.environ.copy()
    ambiente.pop("PYTHONPATH", None)

    processo = subprocess.run(
        [
            sys.executable,
            "-m",
            "reembolso",
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida),
        ],
        cwd=raiz,
        env=ambiente,
        capture_output=True,
        text=True,
        check=False,
    )

    assert processo.returncode == 0, processo.stderr
    assert saida.is_file()
    resultado = json.loads(saida.read_text(encoding="utf-8"))
    assert len(resultado["itens"]) == 14
