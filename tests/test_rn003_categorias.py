from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_03_categorias import filtrar_categorias


def test_rn003_categoria_fora_da_politica_nao_gasta_teto():
    despesas = [
        Despesa(
            id="d-fora",
            data=date(2026, 7, 3),
            categoria="coworking",
            fornecedor="Espaco",
            valor=Decimal("50.00"),
            tem_nota_fiscal=True,
            indice_original=0,
        ),
        Despesa(
            id="d-001",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Restaurante",
            valor=Decimal("50.00"),
            tem_nota_fiscal=True,
            indice_original=1,
        ),
        Despesa(
            id="d-002",
            data=date(2026, 7, 3),
            categoria="alimentacao",
            fornecedor="Cantina",
            valor=Decimal("25.00"),
            tem_nota_fiscal=True,
            indice_original=2,
        ),
    ]

    despesas_pendentes, resultados_recusados = filtrar_categorias(despesas)

    assert [despesa.id for despesa in despesas_pendentes] == ["d-001", "d-002"]
    assert len(resultados_recusados) == 1
    assert resultados_recusados[0].id == "d-fora"
    assert resultados_recusados[0].valor_reembolsavel == Decimal("0.00")
    assert resultados_recusados[0].status == "RECUSADO"
    assert resultados_recusados[0].motivo == "CATEGORIA_FORA_POLITICA"
