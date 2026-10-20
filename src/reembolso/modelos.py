"""Modelos tipados usados pelo motor de reembolso."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal


StatusDespesa = Literal["APROVADO", "PARCIAL", "RECUSADO", "ESTORNO"]


@dataclass
class Colaborador:
    id: str
    nome: str | None = None
    centro_custo: str | None = None


@dataclass
class Periodo:
    inicio: date
    fim: date
    competencia: str | None = None


@dataclass
class Despesa:
    id: str
    data: date
    categoria: str
    fornecedor: str
    valor: Decimal
    tem_nota_fiscal: bool
    indice_original: int
    moeda: str = "BRL"
    valor_original: Decimal | None = None
    taxa_cambio: Decimal | None = None
    data_taxa_cambio: date | None = None
    descricao: str | None = None
    alertas: list[str] = field(default_factory=list)


@dataclass
class EntradaExecucao:
    colaborador: Colaborador
    periodo: Periodo
    despesas: list[Despesa]


@dataclass
class ResultadoDespesa:
    id: str
    valor_solicitado: Decimal
    valor_reembolsavel: Decimal
    status: StatusDespesa
    motivo: str
    alertas: list[str] = field(default_factory=list)
    despesa_mantida: str | None = None
    moeda_original: str | None = None
    valor_original: Decimal | None = None
    taxa_cambio: Decimal | None = None
    data_taxa_cambio: date | None = None


@dataclass
class ResumoExecucao:
    total_solicitado: Decimal
    total_reembolsavel: Decimal
    total_recusado: Decimal
    contagem_por_status: dict[StatusDespesa, int]


@dataclass
class ResultadoExecucao:
    resultados: list[ResultadoDespesa]
    resumo: ResumoExecucao
