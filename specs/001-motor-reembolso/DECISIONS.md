# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-001 — Define validação de entrada inválida · 2026-10-19

**Gatilho:** lacuna encontrada na fase de plano: a spec não definia o comportamento para entradas inválidas.

**O que mudou na spec:** adicionada RN-010 para definir os dados obrigatórios e opcionais, validação completa antes do cálculo, mensagem de erro, ausência de arquivo de saída e códigos de saída.

**Por quê:** estabelecer um comportamento verificável e consistente para entradas inválidas.

**O que isso invalidou:** nada.

**Tasks afetadas:** nenhuma; ainda não existem.

**Custo:** 3 documentos alterados; nenhum código ou teste alterado.

---
