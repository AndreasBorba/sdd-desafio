from datetime import date, timedelta
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_07_viagem import identificar_viagem


def test_rn007_inferencia_viagem_considera_hospedagem_qualificada():
    hospedagens = [
        ("d-2-diarias", date(2026, 7, 1), "Hotel Rio - 2 diarias", 2, False),
        ("d-3-noites", date(2026, 7, 10), "Airbnb 3 noites", 3, False),
        ("d-acentos", date(2026, 7, 20), "Hotel 2 DIÁRIAS", 2, False),
        ("d-sem-espaco", date(2026, 7, 30), "Hotel 2diarias", 2, False),
        ("d-uma-noite", date(2026, 8, 10), "Hotel 1 noite", 1, False),
        ("d-primeiro-trecho", date(2026, 8, 20), "2 diarias e 1 noite", 2, False),
        ("d-ausente", date(2026, 9, 1), "Hospedagem", 1, True),
        ("d-zero", date(2026, 9, 10), "0 noites", 1, True),
        ("d-extenso", date(2026, 9, 20), "duas noites", 1, True),
    ]
    despesas = [
        Despesa(
            id=identificador,
            data=data,
            categoria="hospedagem",
            fornecedor="Hotel",
            valor=Decimal("100.00"),
            tem_nota_fiscal=True,
            indice_original=indice,
            descricao=descricao,
        )
        for indice, (identificador, data, descricao, _, _) in enumerate(hospedagens)
    ]

    dias_viagem, despesas_atualizadas = identificar_viagem(despesas)

    dias_esperados = set()
    for _, inicio, _, noites, _ in hospedagens:
        dias_esperados.update(
            inicio + timedelta(days=deslocamento)
            for deslocamento in range(noites + 1)
        )

    assert dias_viagem == dias_esperados
    assert [despesa.id for despesa in despesas_atualizadas] == [
        despesa.id for despesa in despesas
    ]
    assert [despesa.alertas for despesa in despesas_atualizadas] == [
        [] if not precisa_alerta else ["DIARIAS_NAO_IDENTIFICADAS"]
        for _, _, _, _, precisa_alerta in hospedagens
    ]
    assert all(not despesa.alertas for despesa in despesas)
