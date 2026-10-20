from datetime import date
from decimal import Decimal

from reembolso.modelos import Despesa
from reembolso.regras.etapa_07_viagem import identificar_viagem
from reembolso.regras.etapa_08_tetos import aplicar_tetos


def _despesa(
    identificador,
    dia,
    categoria,
    valor,
    indice,
    descricao=None,
):
    return Despesa(
        id=identificador,
        data=dia,
        categoria=categoria,
        fornecedor=identificador,
        valor=Decimal(valor),
        tem_nota_fiscal=True,
        indice_original=indice,
        descricao=descricao,
    )


def test_rn008_aplica_teto_diario_e_distribui_excedente():
    despesas = [
        _despesa("d-food-second", date(2026, 6, 1), "alimentacao", "20.00", 1),
        _despesa("d-food-first", date(2026, 6, 1), "alimentacao", "50.00", 0),
        _despesa("d-weekend", date(2026, 7, 4), "alimentacao", "70.00", 2),
        _despesa(
            "d-trip",
            date(2026, 7, 1),
            "hospedagem",
            "480.00",
            3,
            "Hotel Rio - 2 diarias",
        ),
        _despesa("d-trip-food", date(2026, 7, 2), "alimentacao", "90.00", 4),
        _despesa("d-trip-transport", date(2026, 7, 3), "transporte_urbano", "130.00", 5),
        _despesa(
            "d-hotel-two",
            date(2026, 8, 1),
            "hospedagem",
            "600.00",
            6,
            "Hotel Rio - 2 diarias",
        ),
        _despesa(
            "d-hotel-three",
            date(2026, 8, 5),
            "hospedagem",
            "800.00",
            7,
            "Airbnb 3 noites",
        ),
        _despesa(
            "d-hotel-accent",
            date(2026, 8, 10),
            "hospedagem",
            "600.00",
            8,
            "Hotel 2 DIÁRIAS",
        ),
        _despesa(
            "d-hotel-no-space",
            date(2026, 8, 15),
            "hospedagem",
            "600.00",
            9,
            "Hotel 2diarias",
        ),
        _despesa(
            "d-hotel-one",
            date(2026, 8, 20),
            "hospedagem",
            "300.00",
            10,
            "Hotel 1 noite",
        ),
        _despesa(
            "d-hotel-first",
            date(2026, 8, 25),
            "hospedagem",
            "600.00",
            11,
            "2 diarias e 1 noite",
        ),
        _despesa(
            "d-hotel-missing",
            date(2026, 9, 1),
            "hospedagem",
            "300.00",
            12,
            "Hospedagem",
        ),
        _despesa(
            "d-hotel-zero",
            date(2026, 9, 5),
            "hospedagem",
            "300.00",
            13,
            "0 noites",
        ),
        _despesa(
            "d-hotel-words",
            date(2026, 9, 10),
            "hospedagem",
            "300.00",
            14,
            "duas noites",
        ),
    ]
    dias_viagem, despesas_com_alertas = identificar_viagem(despesas)

    resultados = aplicar_tetos(despesas_com_alertas, dias_viagem)
    por_id = {resultado.id: resultado for resultado in resultados}

    assert por_id["d-food-first"].valor_reembolsavel == Decimal("50.00")
    assert por_id["d-food-first"].status == "APROVADO"
    assert por_id["d-food-second"].valor_reembolsavel == Decimal("10.00")
    assert por_id["d-food-second"].status == "PARCIAL"
    assert por_id["d-food-second"].motivo == "LIMITE_EXCEDIDO"
    assert por_id["d-weekend"].valor_reembolsavel == Decimal("60.00")
    assert por_id["d-trip-food"].valor_reembolsavel == Decimal("90.00")
    assert por_id["d-trip-food"].status == "APROVADO"
    assert por_id["d-trip-food"].alertas == ["VIAGEM_INFERIDA"]
    assert por_id["d-trip-transport"].valor_reembolsavel == Decimal("120.00")
    assert por_id["d-trip-transport"].status == "PARCIAL"
    assert por_id["d-trip-transport"].alertas == ["VIAGEM_INFERIDA"]
    assert por_id["d-trip"].valor_reembolsavel == Decimal("480.00")

    for identificador, esperado in (
        ("d-hotel-two", "500.00"),
        ("d-hotel-accent", "500.00"),
        ("d-hotel-no-space", "500.00"),
        ("d-hotel-first", "500.00"),
        ("d-hotel-three", "750.00"),
        ("d-hotel-one", "250.00"),
        ("d-hotel-missing", "250.00"),
        ("d-hotel-zero", "250.00"),
        ("d-hotel-words", "250.00"),
    ):
        assert por_id[identificador].valor_reembolsavel == Decimal(esperado)

    for identificador in ("d-hotel-missing", "d-hotel-zero", "d-hotel-words"):
        assert por_id[identificador].alertas == ["DIARIAS_NAO_IDENTIFICADAS"]
