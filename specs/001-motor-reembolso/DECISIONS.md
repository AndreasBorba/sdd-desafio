# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-002 — Identifica noites na descrição de hospedagem · 2026-10-20

**Gatilho:** ambiguidade descoberta na implementação da T-010.

**O que mudou na spec:** AMB-003 e RN-007 agora definem que o número de noites é o primeiro número inteiro maior que zero seguido de "diária", "diárias", "noite" ou "noites", com espaço opcional e sem distinção de maiúsculas ou acentos. Números por extenso não são reconhecidos. Sem trecho válido, considera-se 1 noite e aplica-se o alerta DIARIAS_NAO_IDENTIFICADAS. Foram acrescentados aceites concretos para descrições com 2 e 3 noites, variação de caixa/acentos, ausência de número reconhecido e múltiplos trechos válidos.

**Por quê:** tornar determinística a identificação de noites na descrição e o cálculo do teto e do período de viagem.

**O que isso invalidou:** nada.

**Tasks afetadas:** T-010 e T-011, pois a T-010 identifica as noites para inferência da viagem e a T-011 aplica o teto de hospedagem por noite.

**Custo:** 3 documentos alterados; nenhum código ou teste alterado. Os critérios de aceite de T-010 e T-011 foram atualizados para cobrir os casos definidos.

---

## D-001 — Define validação de entrada inválida · 2026-10-19

**Gatilho:** lacuna encontrada na fase de plano: a spec não definia o comportamento para entradas inválidas.

**O que mudou na spec:** adicionada RN-010 para definir os dados obrigatórios e opcionais, validação completa antes do cálculo, mensagem de erro, ausência de arquivo de saída e códigos de saída.

**Por quê:** estabelecer um comportamento verificável e consistente para entradas inválidas.

**O que isso invalidou:** nada.

**Tasks afetadas:** nenhuma; ainda não existem.

**Custo:** 3 documentos alterados; nenhum código ou teste alterado.

---
