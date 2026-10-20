# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-006 — Define reembolso sob teto com fração de centavo · 2026-10-20

**Gatilho:** implementação da T-025 revelou que a ampliação percentual pode produzir teto com fração de centavo.

**O que mudou na spec:** AMB-034 e RN-008 estabelecem que o teto decimal permanece exato, mas o reembolso fica em centavos e não pode ultrapassar o teto.

**Por quê:** manter precisão decimal no teto sem emitir valor monetário fracionado em centavos nem exceder o limite autorizado.

**O que isso invalidou:** nada.

**Tasks afetadas:** T-025.

**Custo:** registrada a regra em spec, log e cobertura; o teste `test_rn008_periodicidade_e_categoria_definidas_na_politica` cobre teto ampliado com fração de centavo.

---

## D-005 — Define percentual de viagem omitido na política · 2026-10-20

**Gatilho:** implementação da T-025 revelou que RN-008 não especificava o percentual quando a política externa contém somente "padrao".

**O que mudou na spec:** AMB-033 e RN-008 definem que, na ausência de `acrescimo_em_viagem_percentual`, a ampliação em viagem é de 50%.

**Por quê:** manter a equivalência com a política v3 quando o arquivo de política não inclui o percentual.

**O que isso invalidou:** nada.

**Tasks afetadas:** T-025.

**Custo:** registrada a regra em spec, log e cobertura; o mesmo teste cobre a ausência do percentual.

---

## D-004 — Registra o envelope do Dia 2 e a política v4 · 2026-10-20

**Gatilho:** envelope lacrado do Dia 2 (política v4).

**O que mudou na spec:** AMB-019 a AMB-032 definem política externa, seleção por centro de custo, herança de categorias, limite zero, periodicidade, metadados informativos, moeda original, câmbio, arredondamento, duplicatas em moeda estrangeira, campos de saída e viagem inferida. RN-001 a RN-013 e os schemas de entrada e saída foram atualizados; a ordem de aplicação foi substituída pelos dez passos do envelope e foram adicionados os aceites concretos dos arquivos de despesas do Dia 2.

**Por quê:** fazer a especificação refletir a política v4 distribuída em arquivo e os casos de borda do envelope, sem codificar limites no produto.

**O que isso invalidou:** a política constante no código; o teste de ponta a ponta antigo passa a usar uma política equivalente à v3 para manter seus resultados anteriores.

**Tasks afetadas:** T-002, T-016, T-017, T-018, T-019 e T-020, além das novas T-022 a T-030. T-018 conserva o aceite anterior usando política equivalente à v3; as novas tasks cobrem a política externa, câmbio, saída, aceites v3/v4 e documentação.

**Custo:** preencher depois da execução das tasks.

---

## D-003 — Registra a interface fixa da CLI · 2026-10-20

**Gatilho:** interface fixa do enunciado não estava na spec; a primeira implementação usou caminhos posicionais.

**O que mudou na spec:** adicionada RN-011 para fixar o comando `calcular`, as opções obrigatórias `--input` e `--output`, a rejeição de caminhos posicionais e a aplicação dos códigos de saída da RN-010.

**Por quê:** alinhar a interface especificada à interface fixa do enunciado e permitir testes verificáveis de uso correto e incorreto.

**O que isso invalidou:** os critérios de interface das tasks T-017 e T-019, que precisam ser atualizados para a sintaxe nomeada; o teste ponta a ponta da T-018 também deve usar o novo formato.

**Tasks afetadas:** T-017, T-018, T-019 e T-020.

**Custo:** 3 documentos alterados; nenhum código ou teste alterado. A nova task T-020 rastreia a correção da CLI, dos testes de CLI e ponta a ponta e do README.

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
