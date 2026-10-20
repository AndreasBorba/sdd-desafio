import json

import pytest

from reembolso.cli import main


def test_rn011_interface_calcular_input_output(tmp_path):
    entrada = tmp_path / "despesas.json"
    saida = tmp_path / "resultado.json"
    entrada.write_text(
        json.dumps(
            {
                "colaborador": {"id": "c-001"},
                "periodo": {
                    "inicio": "2026-07-01",
                    "fim": "2026-07-31",
                },
                "despesas": [],
            }
        ),
        encoding="utf-8",
    )

    assert main(
        ["calcular", "--input", str(entrada), "--output", str(saida)]
    ) == 0
    assert saida.is_file()

    saida_sem_argumento = tmp_path / "sem-output.json"
    with pytest.raises(SystemExit) as sem_output:
        main(["calcular", "--input", str(entrada)])
    assert sem_output.value.code == 2
    assert not saida_sem_argumento.exists()

    saida_posicional = tmp_path / "posicional.json"
    with pytest.raises(SystemExit) as posicional:
        main(["calcular", str(entrada), str(saida_posicional)])
    assert posicional.value.code == 2
    assert not saida_posicional.exists()
