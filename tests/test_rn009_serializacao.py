import json
from decimal import Decimal

from reembolso.modelos import (
    ResultadoDespesa,
    ResultadoExecucao,
    ResumoExecucao,
)
from reembolso.entrada_saida import serializar_saida


def test_rn009_serializa_itens_e_resumo_no_formato_da_spec():
    resultado = ResultadoExecucao(
        resultados=[
            ResultadoDespesa(
                id="d-001",
                valor_solicitado=Decimal("72.50"),
                valor_reembolsavel=Decimal("60.00"),
                status="PARCIAL",
                motivo="LIMITE_EXCEDIDO",
                alertas=[],
            ),
            ResultadoDespesa(
                id="d-007",
                valor_solicitado=Decimal("54.90"),
                valor_reembolsavel=Decimal("0.00"),
                status="RECUSADO",
                motivo="DUPLICADA",
                despesa_mantida="d-006",
                alertas=[],
            ),
        ],
        resumo=ResumoExecucao(
            total_solicitado=Decimal("127.40"),
            total_reembolsavel=Decimal("60.00"),
            total_recusado=Decimal("67.40"),
            contagem_por_status={
                "APROVADO": 0,
                "PARCIAL": 1,
                "RECUSADO": 1,
                "ESTORNO": 0,
            },
        ),
    )

    texto = serializar_saida(resultado)
    saida = json.loads(texto, parse_float=Decimal)

    assert saida == {
        "itens": [
            {
                "id": "d-001",
                "valor_solicitado": Decimal("72.50"),
                "valor_reembolsavel": Decimal("60.00"),
                "status": "PARCIAL",
                "motivo": "LIMITE_EXCEDIDO",
                "alertas": [],
            },
            {
                "id": "d-007",
                "valor_solicitado": Decimal("54.90"),
                "valor_reembolsavel": Decimal("0.00"),
                "status": "RECUSADO",
                "motivo": "DUPLICADA",
                "despesa_mantida": "d-006",
                "alertas": [],
            },
        ],
        "resumo": {
            "total_solicitado": Decimal("127.40"),
            "total_reembolsavel": Decimal("60.00"),
            "total_recusado": Decimal("67.40"),
            "contagem_por_status": {
                "APROVADO": 0,
                "PARCIAL": 1,
                "RECUSADO": 1,
                "ESTORNO": 0,
            },
        },
    }
    assert '"valor_solicitado": 72.50' in texto
    assert '"total_recusado": 67.40' in texto
    assert '"despesa_mantida": "d-006"' in texto
