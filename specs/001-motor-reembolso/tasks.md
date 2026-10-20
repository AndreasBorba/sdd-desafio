# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar um commit. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque [x] conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): descrição` · `test(T-003): descrição`

---

## Fase 1 — Fundação

- [x] **T-001** — Criar a estrutura do pacote da aplicação e dos testes, separando as fronteiras de entrada, cálculo e saída conforme o plano.
  - **Atende:** RN-001
  - **Aceite:** o teste `test_rn001_pacote_base_e_importavel` passa.
  - **Commit:**

- [x] **T-002** — Centralizar a configuração da política: categorias válidas, tetos, ampliação na viagem e limiar da nota fiscal.
  - **Atende:** RN-008, AMB-001, AMB-002, AMB-003, AMB-004, AMB-008
  - **Aceite:** o teste `test_rn008_configuracao_define_tetos_da_politica` passa.
  - **Commit:**

- [x] **T-003** — Definir os modelos tipados da execução, despesas, resultados por item e resumo, preservando valores monetários decimais e a ordem de entrada.
  - **Atende:** RN-001, RN-009
  - **Aceite:** o teste `test_rn001_modelos_preservam_valores_decimais_e_ordem` passa.
  - **Commit:**

## Fase 2 — Pipeline da política

- [x] **T-004** — Implementar a etapa 1: arredondar o valor uma única vez e normalizar a categoria antes do cálculo.
  - **Atende:** RN-001, AMB-013, AMB-015
  - **Aceite:** o teste `test_rn001_arredonda_valor_e_normaliza_categoria` passa.
  - **Commit:**

- [x] **T-005** — Implementar a etapa 2: separar estornos, atribuindo status e valor reembolsável conforme a spec.
  - **Atende:** RN-002, AMB-014
  - **Aceite:** o teste `test_rn002_estorno_nao_altera_teto` passa.
  - **Commit:**

- [x] **T-006** — Implementar a etapa 3: recusar categorias fora da política sem consumir o teto do dia.
  - **Atende:** RN-003
  - **Aceite:** o teste `test_rn003_categoria_fora_da_politica_nao_gasta_teto` passa.
  - **Commit:**

- [x] **T-007** — Implementar a etapa 4: recusar despesas cuja data esteja fora do período informado, incluindo corretamente as datas-limite.
  - **Atende:** RN-004, AMB-009, AMB-010
  - **Aceite:** o teste `test_rn004_periodo_inclui_inicio_e_fim` passa.
  - **Commit:**

- [x] **T-008** — Implementar a etapa 5: identificar duplicatas pelos campos definidos, manter a primeira ocorrência e recusar as demais sem consumir teto.
  - **Atende:** RN-005, AMB-011, AMB-012
  - **Aceite:** o teste `test_rn005_duplica_recusa_e_identifica_despesa_mantida` passa.
  - **Commit:**

- [x] **T-009** — Implementar a etapa 6: exigir nota fiscal individualmente para valores acima de R$ 100,00 e recusar os itens sem nota antes do cálculo dos tetos.
  - **Atende:** RN-006, AMB-005, AMB-006
  - **Aceite:** o teste `test_rn006_nota_fiscal_por_despesa_e_limite_exato` passa.
  - **Commit:**

- [x] **T-010** — Implementar a etapa 7: inferir os dias de viagem a partir das hospedagens qualificadas, identificando diárias e aplicando os alertas previstos.
  - **Atende:** RN-007, AMB-003, AMB-007
  - **Aceite:** o teste `test_rn007_inferencia_viagem_considera_hospedagem_qualificada` passa.
  - **Aceite de diárias:** o teste reconhece "Hotel Rio - 2 diarias" como 2 noites, "Airbnb 3 noites" como 3, "Hotel 2 DIÁRIAS" como 2, "Hotel 2diarias" como 2, "Hotel 1 noite" como 1 sem alerta e "2 diarias e 1 noite" como 2; "Hospedagem" sem número reconhecido, "0 noites" e "duas noites" resultam em 1 noite e no alerta DIARIAS_NAO_IDENTIFICADAS.
  - **Commit:**

- [x] **T-011** — Implementar a etapa 8: aplicar tetos agregados por dia, limites de viagem e prioridade por data e ordem do arquivo, sem tratamento especial para plantão ou fim de semana.
  - **Atende:** RN-008, AMB-001, AMB-002, AMB-003, AMB-004, AMB-008, AMB-016, AMB-017, AMB-018
  - **Aceite:** o teste `test_rn008_aplica_teto_diario_e_distribui_excedente` passa.
  - **Aceite de hospedagem:** o teste aplica o teto de R$ 250 por noite identificada: "Hotel Rio - 2 diarias" e "Hotel 2diarias" têm teto de R$ 500, "Airbnb 3 noites" tem teto de R$ 750 e "Hotel 1 noite" tem teto de R$ 250 sem alerta; "Hospedagem" sem número reconhecido, "0 noites" e "duas noites" têm teto de R$ 250 e recebem DIARIAS_NAO_IDENTIFICADAS.
  - **Commit:**

- [x] **T-012** — Implementar a etapa 9: calcular totais e contagens por status, excluindo estornos dos totais e contando duplicatas recusadas.
  - **Atende:** RN-009, AMB-012, AMB-014, AMB-018
  - **Aceite:** o teste `test_rn009_calcula_totais_e_contagem_por_status` passa.
  - **Commit:**

## Fase 3 — Entrada inválida

- [x] **T-013** — Validar a presença dos campos obrigatórios antes de iniciar qualquer cálculo e informar o id da despesa quando disponível.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_entrada_invalida_campo_obrigatorio` passa.
  - **Commit:**

- [x] **T-014** — Validar tipos, valores numéricos, datas e a ordem de início e fim do período antes do cálculo.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_entrada_invalida_tipos_datas_e_periodo` passa.
  - **Commit:**

- [x] **T-015** — Tratar arquivo inexistente e JSON malformado como entrada inválida, sem calcular despesas nem gerar saída.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_entrada_invalida_arquivo_e_json` passa.
  - **Commit:**

## Fase 4 — Saída e resumo

- [x] **T-016** — Montar e serializar o JSON de saída com os campos e status definidos, incluindo os resultados por item e o resumo.
  - **Atende:** RN-001, RN-002, RN-005, RN-006, RN-007, RN-008, RN-009
  - **Aceite:** o teste `test_rn009_serializa_itens_e_resumo_no_formato_da_spec` passa.
  - **Commit:**

## Fase 5 — CLI

- [x] **T-017** — Implementar a linha de comando para receber os caminhos de entrada e saída, executar o fluxo e comunicar erros na saída de erro.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_codigos_de_saida` passa.
  - **Commit:**

## Fase 6 — Ponta a ponta e documentação

- [x] **T-018** — Executar a CLI com o JSON de exemplo e verificar os 14 itens, os resultados e os totais esperados na spec.
  - **Atende:** RN-001, RN-002, RN-003, RN-004, RN-005, RN-006, RN-007, RN-008, RN-009
  - **Aceite:** o teste `test_rn009_ponta_a_ponta_json_de_exemplo` passa.
  - **Commit:**

- [ ] **T-019** — Documentar no README como executar e testar o projeto e como usar a CLI com o formato de entrada e saída definido.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_comando_documentado_no_readme` passa.
  - **Commit:**

---

## Cobertura

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-004 | `test_rn001_arredonda_valor_e_normaliza_categoria` |
| RN-002 | T-005 | `test_rn002_estorno_nao_altera_teto` |
| RN-003 | T-006 | `test_rn003_categoria_fora_da_politica_nao_gasta_teto` |
| RN-004 | T-007 | `test_rn004_periodo_inclui_inicio_e_fim` |
| RN-005 | T-008 | `test_rn005_duplica_recusa_e_identifica_despesa_mantida` |
| RN-006 | T-009 | `test_rn006_nota_fiscal_por_despesa_e_limite_exato` |
| RN-007 | T-010 | `test_rn007_inferencia_viagem_considera_hospedagem_qualificada` |
| RN-008 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| RN-009 | T-012 | `test_rn009_calcula_totais_e_contagem_por_status` |
| RN-010 | T-013 | `test_rn010_entrada_invalida_campo_obrigatorio` |
| RN-010 | T-014 | `test_rn010_entrada_invalida_tipos_datas_e_periodo` |
| RN-010 | T-015 | `test_rn010_entrada_invalida_arquivo_e_json` |
| RN-010 | T-017 | `test_rn010_codigos_de_saida` |
| AMB-001 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-002 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-003 | T-010 | `test_rn007_inferencia_viagem_considera_hospedagem_qualificada` |
| AMB-004 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-005 | T-009 | `test_rn006_nota_fiscal_por_despesa_e_limite_exato` |
| AMB-006 | T-009 | `test_rn006_nota_fiscal_por_despesa_e_limite_exato` |
| AMB-007 | T-010 | `test_rn007_inferencia_viagem_considera_hospedagem_qualificada` |
| AMB-008 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-009 | T-007 | `test_rn004_periodo_inclui_inicio_e_fim` |
| AMB-010 | T-007 | `test_rn004_periodo_inclui_inicio_e_fim` |
| AMB-011 | T-008 | `test_rn005_duplica_recusa_e_identifica_despesa_mantida` |
| AMB-012 | T-008 | `test_rn005_duplica_recusa_e_identifica_despesa_mantida` |
| AMB-013 | T-004 | `test_rn001_arredonda_valor_e_normaliza_categoria` |
| AMB-014 | T-005 | `test_rn002_estorno_nao_altera_teto` |
| AMB-015 | T-004 | `test_rn001_arredonda_valor_e_normaliza_categoria` |
| AMB-016 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-017 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| AMB-018 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |

**RN ou AMB sem task:** nenhum.
