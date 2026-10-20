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
  - **Aceite:** o teste `test_rn009_ponta_a_ponta_json_de_exemplo` passa usando uma política equivalente à v3.
  - **Commit:**

- [x] **T-019** — Documentar no README como executar e testar o projeto e como usar a CLI com o formato de entrada e saída definido.
  - **Atende:** RN-010
  - **Aceite:** o teste `test_rn010_comando_documentado_no_readme` passa.
  - **Commit:**

## Fase 7 — Correção de interface

- [x] **T-020** — Ajustar a CLI para `calcular --input <arquivo de despesas> --output <arquivo de resultado>`, atualizar os testes de CLI e de ponta a ponta e atualizar o README para o novo formato.
  - **Atende:** RN-011
  - **Aceite:** o teste `test_rn011_interface_calcular_input_output` passa e a suíte inteira passa.
  - **Commit:**

## Fase 8 — Correção de execução

- [x] **T-021** — Tornar o pacote instalável com `pyproject.toml` usando layout `src/` e documentar no README os passos de instalação, execução e testes no PowerShell.
  - **Atende:** RN-011
  - **Aceite:** após criar e ativar `.venv`, executar `pip install -e .` e `pip install pytest`, o comando `python -m reembolso calcular --input exemplos\despesas-exemplo.json --output resultado.json` funciona a partir da raiz, cria o arquivo e retorna código 0; o teste `test_rn011_comando_executa_a_partir_da_raiz` passa executando o comando em processo separado e sem depender do `pytest.ini`.
  - **README:** documentar em PowerShell a criação e ativação de `.venv`, instalação editável, instalação do pytest, execução da CLI e execução dos testes.
  - **Commit:**

## Fase 5 — Envelope

- [ ] **T-022** — Carregar a política externa e validar JSON, presença de "padrao", limites não negativos e periodicidades conhecidas, lendo os números como `Decimal`.
  - **Atende:** RN-010, RN-012, AMB-019, AMB-024
  - **Aceite:** o teste `test_rn012_carrega_politica_externa_com_validacao_decimal` passa.
  - **Commit:**

- [ ] **T-023** — Adicionar as opções opcionais `--politica` e `--cambio` à CLI e usar os arquivos padrão distribuídos quando forem omitidas.
  - **Atende:** RN-010, RN-011, RN-012, RN-013, AMB-019
  - **Aceite:** o teste `test_rn011_opcoes_politica_cambio_e_padroes` passa.
  - **Commit:**

- [ ] **T-024** — Selecionar limites pelo centro de custo, aplicar a herança de "padrao" e recusar limite zero como categoria fora da política.
  - **Atende:** RN-003, RN-012, AMB-020, AMB-021, AMB-022
  - **Aceite:** o teste `test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero` passa.
  - **Commit:**

- [ ] **T-025** — Aplicar periodicidades "dia" e "diaria" para categorias da política e aceitar categorias definidas no arquivo, mantendo a ampliação de viagem somente para alimentação e transporte_urbano.
  - **Atende:** RN-007, RN-008, RN-012, AMB-003, AMB-023
  - **Aceite:** o teste `test_rn008_periodicidade_e_categoria_definidas_na_politica` passa.
  - **Commit:**

- [ ] **T-026** — Resolver a cotação pela data da despesa ou pela mais recente nos cinco dias anteriores, converter e arredondar em BRL uma única vez e tratar indisponibilidade de câmbio.
  - **Atende:** RN-001, RN-006, RN-010, RN-013, AMB-025, AMB-026, AMB-027
  - **Aceite:** o teste `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` passa.
  - **Commit:**

- [ ] **T-027** — Incluir moeda e valor original na identificação de duplicatas.
  - **Atende:** RN-005, AMB-028
  - **Aceite:** o teste `test_rn005_duplicata_exige_mesma_moeda_e_valor_original` passa.
  - **Commit:**

- [ ] **T-028** — Serializar os campos de moeda original e de câmbio apenas nos itens estrangeiros aplicáveis, mantendo valores solicitados e reembolsáveis em BRL e sem converter estornos estrangeiros ou itens sem cotação.
  - **Atende:** RN-002, RN-009, RN-013, AMB-029, AMB-031, AMB-032
  - **Aceite:** o teste `test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao` passa.
  - **Commit:**

- [ ] **T-029** — Validar ponta a ponta o resultado v3 preservado e a política v4 nos três arquivos de despesas definidos no envelope.
  - **Atende:** RN-001 a RN-013, AMB-019 a AMB-030
  - **Aceite:** o teste `test_rn009_ponta_a_ponta_envelope_v3_e_v4` passa.
  - **Commit:**

- [ ] **T-030** — Atualizar o README com as opções de política e câmbio, os arquivos padrão e o comportamento da moeda estrangeira.
  - **Atende:** RN-011, RN-013, AMB-019, AMB-025 a AMB-029
  - **Aceite:** o teste `test_rn011_readme_documenta_politica_cambio_e_moeda` passa.
  - **Commit:**

---

## Cobertura

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-004 | `test_rn001_arredonda_valor_e_normaliza_categoria` |
| RN-001 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| RN-002 | T-005 | `test_rn002_estorno_nao_altera_teto` |
| RN-003 | T-006 | `test_rn003_categoria_fora_da_politica_nao_gasta_teto` |
| RN-004 | T-007 | `test_rn004_periodo_inclui_inicio_e_fim` |
| RN-005 | T-008 | `test_rn005_duplica_recusa_e_identifica_despesa_mantida` |
| RN-005 | T-027 | `test_rn005_duplicata_exige_mesma_moeda_e_valor_original` |
| RN-006 | T-009 | `test_rn006_nota_fiscal_por_despesa_e_limite_exato` |
| RN-007 | T-010 | `test_rn007_inferencia_viagem_considera_hospedagem_qualificada` |
| RN-008 | T-011 | `test_rn008_aplica_teto_diario_e_distribui_excedente` |
| RN-009 | T-012 | `test_rn009_calcula_totais_e_contagem_por_status` |
| RN-010 | T-013 | `test_rn010_entrada_invalida_campo_obrigatorio` |
| RN-010 | T-014 | `test_rn010_entrada_invalida_tipos_datas_e_periodo` |
| RN-010 | T-015 | `test_rn010_entrada_invalida_arquivo_e_json` |
| RN-010 | T-017 | `test_rn010_codigos_de_saida` |
| RN-010 | T-022 | `test_rn012_carrega_politica_externa_com_validacao_decimal` |
| RN-010 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| RN-011 | T-020 | `test_rn011_interface_calcular_input_output` |
| RN-011 | T-021 | `test_rn011_comando_executa_a_partir_da_raiz` |
| RN-011 | T-023 | `test_rn011_opcoes_politica_cambio_e_padroes` |
| RN-011 | T-030 | `test_rn011_readme_documenta_politica_cambio_e_moeda` |
| RN-012 | T-022 | `test_rn012_carrega_politica_externa_com_validacao_decimal` |
| RN-012 | T-024 | `test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero` |
| RN-012 | T-025 | `test_rn008_periodicidade_e_categoria_definidas_na_politica` |
| RN-013 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| RN-013 | T-028 | `test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao` |
| RN-013 | T-029 | `test_rn009_ponta_a_ponta_envelope_v3_e_v4` |
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
| AMB-019 | T-022 | `test_rn012_carrega_politica_externa_com_validacao_decimal` |
| AMB-019 | T-023 | `test_rn011_opcoes_politica_cambio_e_padroes` |
| AMB-020 | T-024 | `test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero` |
| AMB-021 | T-024 | `test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero` |
| AMB-022 | T-024 | `test_rn003_politica_por_centro_de_custo_herda_padrao_e_recusa_limite_zero` |
| AMB-023 | T-025 | `test_rn008_periodicidade_e_categoria_definidas_na_politica` |
| AMB-024 | T-022 | `test_rn012_carrega_politica_externa_com_validacao_decimal` |
| AMB-025 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| AMB-026 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| AMB-027 | T-026 | `test_rn013_converte_moeda_com_arredondamento_e_janela_de_cambio` |
| AMB-028 | T-027 | `test_rn005_duplicata_exige_mesma_moeda_e_valor_original` |
| AMB-029 | T-028 | `test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao` |
| AMB-030 | T-029 | `test_rn009_ponta_a_ponta_envelope_v3_e_v4` |
| AMB-031 | T-028 | `test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao` |
| AMB-032 | T-028 | `test_rn013_serializa_campos_de_moeda_sem_taxa_quando_sem_conversao` |

**RN ou AMB sem task:** nenhum.
