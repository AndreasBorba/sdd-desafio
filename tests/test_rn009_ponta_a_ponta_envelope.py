import json
import os
from decimal import Decimal
from pathlib import Path
import subprocess
import sys


def _executar(raiz, entrada, saida, politica, cambio):
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
            "--politica",
            str(politica),
            "--cambio",
            str(cambio),
        ],
        cwd=raiz,
        env=ambiente,
        capture_output=True,
        text=True,
        check=False,
    )
    assert processo.returncode == 0, processo.stderr
    assert processo.stderr == ""
    return json.loads(saida.read_text(encoding="utf-8"), parse_float=Decimal)


def _conferir(resultado, esperados, totais, contagem):
    itens = resultado["itens"]
    assert [
        (
            item["id"],
            item["status"],
            item["valor_reembolsavel"],
            item["motivo"],
        )
        for item in itens
    ] == esperados
    resumo = resultado["resumo"]
    assert (
        resumo["total_solicitado"],
        resumo["total_reembolsavel"],
        resumo["total_recusado"],
    ) == totais
    assert resumo["contagem_por_status"] == contagem


def test_rn009_ponta_a_ponta_envelope_v3_e_v4(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    exemplos = raiz / "exemplos"
    envelope = exemplos / "envelope"
    politica = envelope / "politica-v4.json"
    cambio = envelope / "cambio.json"
    contagem_comercial = {
        "APROVADO": 4,
        "PARCIAL": 3,
        "RECUSADO": 3,
        "ESTORNO": 0,
    }
    resultado_comercial = _executar(
        raiz,
        envelope / "despesas-envelope.json",
        tmp_path / "comercial.json",
        politica,
        cambio,
    )
    _conferir(
        resultado_comercial,
        [
            ("e-001", "PARCIAL", Decimal("300.00"), "LIMITE_EXCEDIDO"),
            ("e-002", "PARCIAL", Decimal("90.00"), "LIMITE_EXCEDIDO"),
            ("e-003", "APROVADO", Decimal("85.26"), ""),
            ("e-004", "PARCIAL", Decimal("90.00"), "LIMITE_EXCEDIDO"),
            ("e-005", "RECUSADO", Decimal("0.00"), "NF_AUSENTE"),
            ("e-006", "RECUSADO", Decimal("0.00"), "CAMBIO_INDISPONIVEL"),
            ("e-007", "APROVADO", Decimal("1200.00"), ""),
            ("e-008", "APROVADO", Decimal("95.00"), ""),
            ("e-009", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
            ("e-010", "APROVADO", Decimal("88.00"), ""),
        ],
        (
            Decimal("2457.52"),
            Decimal("1948.26"),
            Decimal("509.26"),
        ),
        contagem_comercial,
    )

    resultado_padrao = _executar(
        raiz,
        envelope / "despesas-envelope-cc-desconhecido.json",
        tmp_path / "padrao.json",
        politica,
        cambio,
    )
    _conferir(
        resultado_padrao,
        [
            ("f-001", "APROVADO", Decimal("58.00"), ""),
            ("f-002", "PARCIAL", Decimal("250.00"), "LIMITE_EXCEDIDO"),
            ("f-003", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
            ("f-004", "APROVADO", Decimal("65.76"), ""),
        ],
        (Decimal("623.76"), Decimal("373.76"), Decimal("250.00")),
        {
            "APROVADO": 2,
            "PARCIAL": 1,
            "RECUSADO": 1,
            "ESTORNO": 0,
        },
    )

    resultado_eng = _executar(
        raiz,
        exemplos / "despesas-exemplo.json",
        tmp_path / "engenharia.json",
        politica,
        cambio,
    )
    _conferir(
        resultado_eng,
        [
            ("d-001", "APROVADO", Decimal("72.50"), ""),
            ("d-002", "PARCIAL", Decimal("2.50"), "LIMITE_EXCEDIDO"),
            ("d-003", "PARCIAL", Decimal("80.00"), "LIMITE_EXCEDIDO"),
            ("d-004", "RECUSADO", Decimal("0.00"), "NF_AUSENTE"),
            ("d-005", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
            ("d-006", "APROVADO", Decimal("54.90"), ""),
            ("d-007", "RECUSADO", Decimal("0.00"), "DUPLICADA"),
            ("d-008", "RECUSADO", Decimal("0.00"), "FORA_COMPETENCIA"),
            ("d-009", "ESTORNO", Decimal("0.00"), "ESTORNO"),
            ("d-010", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
            ("d-011", "APROVADO", Decimal("33.33"), ""),
            ("d-012", "APROVADO", Decimal("47.20"), ""),
            ("d-013", "RECUSADO", Decimal("0.00"), "CATEGORIA_FORA_POLITICA"),
            ("d-014", "APROVADO", Decimal("61.00"), ""),
        ],
        (
            Decimal("1861.84"),
            Decimal("351.43"),
            Decimal("1510.41"),
        ),
        {
            "APROVADO": 5,
            "PARCIAL": 2,
            "RECUSADO": 6,
            "ESTORNO": 1,
        },
    )
