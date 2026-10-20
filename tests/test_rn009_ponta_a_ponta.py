import json
import os
from pathlib import Path
import subprocess
import sys
from decimal import Decimal


def test_rn009_ponta_a_ponta_json_de_exemplo(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    entrada = raiz / "exemplos" / "despesas-exemplo.json"
    saida = tmp_path / "resultado.json"
    ambiente = os.environ.copy()
    caminho_src = str(raiz / "src")
    ambiente["PYTHONPATH"] = os.pathsep.join(
        filtro
        for filtro in (caminho_src, ambiente.get("PYTHONPATH", ""))
        if filtro
    )

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
    assert processo.stderr == ""
    resultado = json.loads(saida.read_text(encoding="utf-8"), parse_float=Decimal)

    esperados = [
        ("d-001", "PARCIAL", Decimal("60.00"), "LIMITE_EXCEDIDO"),
        ("d-002", "RECUSADO", Decimal("0.00"), "LIMITE_EXCEDIDO"),
        ("d-003", "PARCIAL", Decimal("80.00"), "LIMITE_EXCEDIDO"),
        ("d-004", "RECUSADO", Decimal("0.00"), "NF_AUSENTE"),
        ("d-005", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
        ("d-006", "APROVADO", Decimal("54.90"), ""),
        ("d-007", "RECUSADO", Decimal("0.00"), "DUPLICADA"),
        ("d-008", "RECUSADO", Decimal("0.00"), "FORA_COMPETENCIA"),
        ("d-009", "ESTORNO", Decimal("0.00"), "ESTORNO"),
        ("d-010", "APROVADO", Decimal("480.00"), ""),
        ("d-011", "APROVADO", Decimal("33.33"), ""),
        ("d-012", "APROVADO", Decimal("47.20"), ""),
        ("d-013", "RECUSADO", Decimal("0.00"), "NF_AUSENTE"),
        ("d-014", "PARCIAL", Decimal("60.00"), "LIMITE_EXCEDIDO"),
    ]
    itens = resultado["itens"]
    assert len(itens) == 14
    assert [
        (
            item["id"],
            item["status"],
            item["valor_reembolsavel"],
            item["motivo"],
        )
        for item in itens
    ] == esperados
    assert itens[6]["despesa_mantida"] == "d-006"
    assert "VALOR_ARREDONDADO" in itens[10]["alertas"]

    resumo = resultado["resumo"]
    assert resumo["total_solicitado"] == Decimal("1861.84")
    assert resumo["total_reembolsavel"] == Decimal("815.43")
    assert resumo["total_recusado"] == Decimal("1046.41")
    assert resumo["contagem_por_status"] == {
        "APROVADO": 4,
        "PARCIAL": 3,
        "RECUSADO": 6,
        "ESTORNO": 1,
    }
