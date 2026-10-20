# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** rascunho · **Última alteração:** 2026-10-19

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o documento de plano.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

## Glossário

- Teto: valor máximo que a empresa paga em uma categoria.
- Agregado: somado. "Teto agregado por dia" é um teto único para todas as despesas daquela categoria no mesmo dia.
- Elegível: despesa que passou nas verificações e pode ser paga.
- Recusada: despesa que a empresa não paga, com valor reembolsável 0.
- Parcial: despesa paga só até o teto, com o excedente cortado.
- Estorno: valor devolvido ao colaborador; aparece como número negativo.
- Competência: o período a que a despesa pertence, como julho.
- Duplicata: o mesmo gasto lançado duas vezes.
- Nota fiscal: o comprovante da compra.

---

## 1. Problema

A empresa precisa decidir, item por item, quanto paga de cada despesa de um colaborador. Hoje isso é feito manualmente e pode variar por erro de leitura, conflito de regras e falta de alinhamento com a política.

A tarefa do sistema é aplicar a política de forma consistente, registrar o motivo de cada decisão e devolver um resultado claro para o financeiro.

## 2. Objetivo

O sistema passa a calcular, para um colaborador e um período, quais despesas são aprovadas, parciais, recusadas ou estorno, e qual valor da empresa deve pagar.

## 3. Fora de escopo

- Não implementa fila de aprovação manual nem alçada; valores acima de R$ 500 continuam aprovados automaticamente, conforme o item C opcional do comunicado.
- Não confere o conteúdo da nota fiscal, só se ela existe.
- Processa um colaborador e um período por execução.
- Não guarda dados nem tem tela; só linha de comando.
- Não cria exceções por plantão, feriado ou cargo.
- Não liga o estorno à despesa original.

## 4. Entrada e saída

**Entrada:** conforme o arquivo de exemplo de despesas. Ela contém um colaborador, um período e uma lista de despesas. O período é definido por `inicio` e `fim`, incluindo as duas datas; `competencia` é apenas um rótulo. Uma despesa fora do período é RECUSADO, motivo FORA_COMPETENCIA.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| colaborador.id | texto | identificador do colaborador | obrigatório |
| colaborador.nome | texto | nome do colaborador | opcional |
| colaborador.centro_custo | texto | centro de custo do colaborador; seleciona a política correspondente, ignorando maiúsculas e espaços nas pontas; se ausente ou sem entrada na política, usa "padrao" | opcional |
| periodo.competencia | texto | rótulo da competência | opcional |
| periodo.inicio | data | primeiro dia do período, incluído | obrigatório |
| periodo.fim | data | último dia do período, incluído | obrigatório |
| despesas[].id | texto | identificador da despesa | obrigatório |
| despesas[].data | data | dia em que a despesa ocorreu | obrigatório |
| despesas[].categoria | texto | categoria da despesa | obrigatório |
| despesas[].descricao | texto | resumo do gasto; se ausente em hospedagem, recebe o alerta DIARIAS_NAO_IDENTIFICADAS | opcional |
| despesas[].fornecedor | texto | nome do fornecedor ou local da compra | obrigatório |
| despesas[].valor | número | valor informado para a despesa | obrigatório |
| despesas[].moeda | texto | moeda original em três letras ISO 4217, ignorando maiúsculas e espaços nas pontas; ausente significa BRL | opcional |
| despesas[].tem_nota_fiscal | booleano | indica se existe nota fiscal | obrigatório |

**Saída:** `valor_solicitado` e `valor_reembolsavel` são sempre valores em BRL. Cada item recebe o status final, o motivo e os alertas. Itens em moeda estrangeira trazem `moeda_original` e `valor_original`; itens em moeda estrangeira convertidos também trazem `taxa_cambio` e `data_taxa_cambio`. Estornos em moeda estrangeira não são convertidos e não trazem taxa nem data de câmbio. O resumo traz a soma dos valores em BRL e a contagem por status.

| Campo | Tipo | Significado |
|---|---|---|
| id | texto | identificador da despesa |
| valor_solicitado | número | valor solicitado em BRL, arredondado para duas casas decimais |
| valor_reembolsavel | número | valor que a empresa paga em BRL |
| status | texto | APROVADO, PARCIAL, RECUSADO ou ESTORNO |
| motivo | texto | vazio para APROVADO; LIMITE_EXCEDIDO para PARCIAL; CATEGORIA_FORA_POLITICA, CAMBIO_INDISPONIVEL, FORA_COMPETENCIA, DUPLICADA, NF_AUSENTE ou LIMITE_EXCEDIDO para RECUSADO; ESTORNO para ESTORNO. Se houver mais de um motivo de recusa, vale o da primeira regra da ordem de aplicação que recusou o item. |
| despesa_mantida | texto | id da despesa mantida; aparece apenas quando o motivo é DUPLICADA |
| alertas | lista | alertas da despesa, como VIAGEM_INFERIDA, DIARIAS_NAO_IDENTIFICADAS ou VALOR_ARREDONDADO |
| moeda_original | texto | moeda ISO 4217 original; aparece apenas em itens originalmente em moeda estrangeira |
| valor_original | número | valor original na moeda informada; aparece apenas em itens originalmente em moeda estrangeira |
| taxa_cambio | número | taxa aplicada à conversão para BRL; aparece apenas em itens em moeda estrangeira convertidos |
| data_taxa_cambio | data | data da cotação aplicada; aparece apenas em itens em moeda estrangeira convertidos |
| total_solicitado | número | soma dos valores solicitados em BRL dos itens que não são estorno |
| total_reembolsavel | número | soma dos valores reembolsáveis em BRL |
| total_recusado | número | total_solicitado menos total_reembolsavel, em BRL, incluindo recusas inteiras e excedentes cortados nos itens PARCIAL; estornos não entram |
| contagem_por_status | objeto | quantidade de itens por status, incluindo estornos |

Exemplo de entrada e saída (subconjunto de 7 despesas, usando uma política equivalente à v3):

**Entrada (trecho do arquivo de exemplo):**

```json
{
  "colaborador": {
    "id": "c-0417",
    "nome": "Marina Volpi"
  },
  "periodo": {
    "competencia": "2026-07",
    "inicio": "2026-07-01",
    "fim": "2026-07-31"
  },
  "despesas": [
    {"id": "d-001", "data": "2026-07-03", "categoria": "alimentacao", "descricao": "Almoco com cliente", "fornecedor": "Restaurante Tavola", "valor": 72.50, "tem_nota_fiscal": true},
    {"id": "d-002", "data": "2026-07-03", "categoria": "alimentacao", "descricao": "Jantar apos reuniao", "fornecedor": "Cantina do Porto", "valor": 38.00, "tem_nota_fiscal": true},
    {"id": "d-006", "data": "2026-07-09", "categoria": "alimentacao", "descricao": "Almoco", "fornecedor": "Bistro Central", "valor": 54.90, "tem_nota_fiscal": true},
    {"id": "d-009", "data": "2026-07-11", "categoria": "transporte_urbano", "descricao": "Estorno de corrida cancelada", "fornecedor": "TaxiApp", "valor": -45.00, "tem_nota_fiscal": false},
    {"id": "d-010", "data": "2026-07-14", "categoria": "hospedagem", "descricao": "Hotel Rio - 2 diarias", "fornecedor": "Hotel Copa Sul", "valor": 480.00, "tem_nota_fiscal": true},
    {"id": "d-011", "data": "2026-07-15", "categoria": "alimentacao", "descricao": "Cafe da manha hotel", "fornecedor": "Hotel Copa Sul", "valor": 33.333, "tem_nota_fiscal": true},
    {"id": "d-014", "data": "2026-07-31", "categoria": "ALIMENTACAO", "descricao": "Jantar de encerramento", "fornecedor": "Restaurante Tavola", "valor": 61.00, "tem_nota_fiscal": true}
  ]
}
```

**Saída esperada (forma do resultado):**

```json
{
  "itens": [
    {"id": "d-001", "valor_solicitado": 72.50, "valor_reembolsavel": 60.00, "status": "PARCIAL", "motivo": "LIMITE_EXCEDIDO", "alertas": []},
    {"id": "d-002", "valor_solicitado": 38.00, "valor_reembolsavel": 0.00, "status": "RECUSADO", "motivo": "LIMITE_EXCEDIDO", "alertas": []},
    {"id": "d-006", "valor_solicitado": 54.90, "valor_reembolsavel": 54.90, "status": "APROVADO", "motivo": "", "alertas": []},
    {"id": "d-009", "valor_solicitado": -45.00, "valor_reembolsavel": 0.00, "status": "ESTORNO", "motivo": "ESTORNO", "alertas": []},
    {"id": "d-010", "valor_solicitado": 480.00, "valor_reembolsavel": 480.00, "status": "APROVADO", "motivo": "", "alertas": []},
    {"id": "d-011", "valor_solicitado": 33.33, "valor_reembolsavel": 33.33, "status": "APROVADO", "motivo": "", "alertas": ["VALOR_ARREDONDADO"]},
    {"id": "d-014", "valor_solicitado": 61.00, "valor_reembolsavel": 60.00, "status": "PARCIAL", "motivo": "LIMITE_EXCEDIDO", "alertas": []}
  ],
  "resumo": {
    "total_solicitado": 739.73,
    "total_reembolsavel": 688.23,
    "total_recusado": 51.50,
    "contagem_por_status": {
      "APROVADO": 3,
      "PARCIAL": 2,
      "RECUSADO": 1,
      "ESTORNO": 1
    }
  }
}
```

## 5. Regras de negócio

Cada regra recebe um ID (`RN-001`, ...). As tasks vão referenciar esses IDs.

### RN-001 — Ajuste inicial da despesa

**Regra:** antes do cálculo, o valor em BRL é arredondado para duas casas decimais, meio para cima, e a categoria é normalizada ignorando maiúsculas, acentos e espaços nas pontas. Para moeda estrangeira, preserva-se o valor original para a conversão; o valor convertido em BRL é arredondado uma única vez conforme RN-013. A moeda é normalizada ignorando maiúsculas e espaços nas pontas, e o centro de custo é comparado ignorando maiúsculas e espaços nas pontas.
**Origem:** decisões AMB-013, AMB-015, AMB-020, AMB-025 e AMB-027
**Aceite:** o item d-011, com valor 33.333 BRL, entra como 33.33 e recebe o alerta VALOR_ARREDONDADO; a categoria "ALIMENTACAO" é tratada como "alimentacao"; moeda " usd " é tratada como "USD" e centro de custo " CC-ENG " como "CC-ENG".

### RN-002 — Estorno

**Regra:** despesa com valor negativo é um estorno. Ela recebe status ESTORNO, valor reembolsável 0 e não altera o teto do dia. Estorno em moeda estrangeira não é convertido e tem `valor_solicitado` 0.00 em BRL.
**Origem:** decisões AMB-014 e AMB-029
**Aceite:** d-009 tem valor -45.00, fica ESTORNO e não entra em nenhum total de solicitado, reembolsável ou recusado.

### RN-003 — Categoria fora da política

**Regra:** a política aplicável é a do centro de custo do colaborador. Se o centro de custo não vier na entrada ou não existir na tabela da política, usa-se "padrao". Categoria ausente na política do centro de custo herda o limite da mesma categoria em "padrao". Se também não existir em "padrao", a categoria está fora da política. Categoria fora da política ou com limite 0 é recusada com motivo CATEGORIA_FORA_POLITICA no mesmo passo, sem pagamento e sem gasto de teto.
**Origem:** políticas e ordem de aplicação, AMB-001, AMB-002, AMB-003, AMB-016 e AMB-020 a AMB-022
**Aceite:** d-005, categoria coworking, é recusada antes do cálculo do teto; não recebe valor e não contabiliza no limite do dia. Um centro de custo sem entrada usa a política "padrao"; uma categoria ausente no centro de custo herda o limite de "padrao"; uma categoria com limite 0 é RECUSADO com CATEGORIA_FORA_POLITICA.

### RN-004 — Período da competência

**Regra:** a despesa vale pela data em que ocorreu. Fora do período informado, a despesa é recusada com motivo FORA_COMPETENCIA.
**Origem:** decisão AMB-009 e AMB-010
**Aceite:** d-008, data 2026-04-15, está fora do período de competência 2026-07 e é recusada.

### RN-005 — Duplicata

**Regra:** duas despesas são duplicatas quando têm a mesma data, categoria, fornecedor, moeda e valor original. A primeira ocorrência paga; as demais são recusadas com motivo DUPLICADA.
**Origem:** decisões AMB-011, AMB-012 e AMB-028
**Aceite:** d-006 e d-007 têm mesmo dia, categoria, fornecedor, moeda e valor original. d-006 é mantida e d-007 retorna RECUSADO com motivo DUPLICADA e `despesa_mantida` igual a "d-006"; despesas que diferem em moeda ou valor original não são duplicatas.

### RN-006 — Nota fiscal obrigatória

**Regra:** despesa com valor solicitado em BRL maior que R$ 100,00 exige nota fiscal. Para moeda estrangeira, compara-se o valor convertido em BRL. Se não houver nota, o item inteiro é recusado, valor reembolsável 0 e não gasta teto.
**Origem:** decisões AMB-005 e AMB-006
**Aceite:** R$ 100,00 em BRL não exige nota; d-003 fica PARCIAL, com valor reembolsável 80.00 e motivo LIMITE_EXCEDIDO. d-004 e d-013 ficam RECUSADO com motivo NF_AUSENTE. Para uma despesa em moeda estrangeira, a exigência é decidida pelo valor convertido em BRL.

### RN-007 — Viagem inferida

**Regra:** se existe uma hospedagem não recusada nos passos anteriores à inferência de viagem na ordem de aplicação, o colaborador está em viagem do dia da despesa até esse dia mais o número de noites, inclusive. Para identificar as noites, considera-se o primeiro número inteiro maior que zero seguido de "diária", "diárias", "noite" ou "noites", com espaço opcional entre o número e a palavra, ignorando maiúsculas e acentos. Números por extenso não são reconhecidos. Se não houver trecho válido, considera-se 1 noite e a hospedagem recebe o alerta DIARIAS_NAO_IDENTIFICADAS. Hospedagem com status PARCIAL também conta. Despesa em moeda estrangeira não gera dia de viagem. O alerta VIAGEM_INFERIDA aparece apenas em item de alimentação ou transporte_urbano, em moeda BRL, em dia de viagem, com valor reembolsável maior que o teto-base.
**Origem:** decisões AMB-007, AMB-008 e AMB-030
**Aceite:** d-010, hospedagem de 2 diárias, torna os dias 2026-07-14, 2026-07-15 e 2026-07-16 de viagem. d-011 está em dia de viagem, mas não recebe VIAGEM_INFERIDA porque seu valor reembolsável de 33.33 não supera o teto-base de alimentação de 60.00. "Hotel Rio - 2 diarias" identifica 2 noites; "Airbnb 3 noites" identifica 3 noites; "Hotel 2 DIÁRIAS" identifica 2 noites; "Hospedagem" identifica 1 noite e recebe DIARIAS_NAO_IDENTIFICADAS; "2 diarias e 1 noite" identifica 2 noites.

### RN-008 — Teto diário e pagamento parcial

**Regra:** os limites e a periodicidade vêm da política selecionada. Periodicidade "dia" significa teto agregado por categoria e dia; cada despesa recebe até o que sobrou do dia. Periodicidade "diaria" significa limite multiplicado pelo número de noites identificado para aquela despesa, conforme AMB-003. Quando a compra passar do teto, a empresa paga até o limite e corta o excedente; as despesas seguintes que excederem o teto ficam RECUSADO com LIMITE_EXCEDIDO. Em viagem, somente alimentação e transporte_urbano têm seus limites ampliados pelo percentual da política. Hospedagem, representacao e o limiar da nota fiscal não são ampliados.
**Origem:** decisões AMB-001, AMB-002, AMB-003, AMB-004, AMB-017, AMB-018 e AMB-023
**Aceite:** com uma política equivalente à v3, no dia 2026-07-03, d-001, com alimentação de 72.50, paga 60.00 e fica PARCIAL; d-002 não recebe valor porque o restante do dia já foi usado.

### RN-009 — Resumo final

**Regra:** o resumo da execução conta em BRL os valores solicitados, os valores reembolsáveis e a contagem final dos itens por status. Estornos não entram nos totais do resumo e duplicatas não gastam teto.
**Origem:** decisões AMB-012 e AMB-014
**Aceite:** d-009 não entra em total_solicitado, total_reembolsavel nem total_recusado; no caso completo d-001 a d-014 usando uma política equivalente à v3, total_solicitado é 1861.84, total_reembolsavel é 815.43, total_recusado é 1046.41 e a contagem é 4 aprovados, 3 parciais, 6 recusados e 1 estorno.

### RN-010 — Validação da entrada

**Regra:** o sistema valida todos os dados antes de calcular. Arquivo de despesas, política ou câmbio inexistente, JSON malformado, campo obrigatório ausente, tipo inválido, valor não numérico, moeda inválida, data inválida, período com início posterior ao fim, limite negativo, periodicidade desconhecida ou política sem "padrao" tornam a entrada inválida. Nesse caso, não é calculada nenhuma despesa nem gerado arquivo de saída; uma mensagem em português é escrita na saída de erro, incluindo o id da despesa quando disponível, e o código de saída é 1. Em caso de sucesso, o código de saída é 0. Erro de uso da linha de comando retorna código 2. Os campos obrigatórios e opcionais são os indicados na tabela de entrada.
**Origem:** decisão de validação da entrada.
**Aceite:** um JSON com uma despesa de id "d-001" sem o campo "valor" retorna código 1, escreve uma mensagem em português que cita "d-001" na saída de erro e não cria o arquivo de saída. Um arquivo de política inválido, sem "padrao", com limite negativo ou periodicidade desconhecida, e uma moeda que não tenha três letras ISO 4217 válida também retornam código 1 e não criam a saída.

### RN-011 — Interface de linha de comando

**Regra:** o comando chama-se `calcular` e recebe `--input` (obrigatório, caminho do arquivo de despesas) e `--output` (obrigatório, caminho do arquivo de resultado), além de `--politica` e `--cambio` opcionais. Se forem omitidas, usa a política e a tabela de câmbio padrão distribuídas com o projeto. Aplicam-se os códigos de saída da RN-010: 0 em caso de sucesso, 1 para entrada inválida e 2 para erro de uso, incluindo a ausência de `--input` ou `--output`. Caminhos posicionais não são aceitos.
**Origem:** interface fixa do enunciado.
**Aceite:** com `calcular --input despesas.json --output resultado.json` e uma entrada válida, o arquivo de saída é criado usando os arquivos padrão e o código de saída é 0; com `--politica politica.json --cambio cambio.json`, os arquivos informados são usados; sem `--output`, o código é 2 e nenhum arquivo de saída é criado; caminhos posicionais não são aceitos.

### RN-012 — Política externa

**Regra:** os limites e a periodicidade são lidos de um arquivo de política, não definidos pelo código. A política contém "padrao"; pode conter políticas por centro de custo. Centro de custo ausente ou sem entrada usa "padrao". Categoria não listada na política do centro de custo herda o limite da mesma categoria em "padrao"; se não existir em "padrao", é categoria fora da política. Limite 0 torna a categoria não reembolsável, recusada com CATEGORIA_FORA_POLITICA no passo de categoria. Limites negativos, periodicidade desconhecida, arquivo ausente, JSON inválido ou ausência de "padrao" invalidam a entrada conforme RN-010. Os números do arquivo são valores monetários decimais. `versao` e `vigencia` são informativos e não entram no cálculo.
**Origem:** decisões AMB-019 a AMB-024
**Aceite:** a política v4 aplicada a despesas com centro de custo CC-ENG-PLATAFORMA produz para d-001 APROVADO 72.50, para d-002 PARCIAL 2.50 e para d-003 PARCIAL 80.00; d-010 e d-013 são recusadas por CATEGORIA_FORA_POLITICA e d-014 é APROVADO 61.00. No caso completo, os totais são 1861.84 / 351.43 / 1510.41 e a contagem é 5 aprovados, 2 parciais, 6 recusados e 1 estorno. Uma política contendo somente "padrao" equivale à política v3 para o arquivo de exemplo.

### RN-013 — Moeda e conversão

**Regra:** moeda é opcional e, quando ausente, é BRL. A moeda informada deve ser um código ISO 4217 de três letras, normalizado ignorando maiúsculas e espaços nas pontas; formato inválido torna a entrada inválida conforme RN-010. A conversão usa a cotação da data da despesa; se não houver cotação nessa data, usa-se a cotação mais recente nos cinco dias corridos anteriores. Sem cotação para a moeda ou fora dessa janela, o item é RECUSADO com motivo CAMBIO_INDISPONIVEL e `valor_solicitado` 0.00. O valor convertido é o valor original multiplicado pela taxa e arredondado uma única vez para duas casas decimais, meio para cima; se o arredondamento alterar o valor, o item recebe VALOR_ARREDONDADO. Tetos e limiar da nota fiscal são comparados em BRL. Despesa em BRL não é convertida. Os valores solicitados e reembolsáveis, bem como os totais, são sempre em BRL. Itens estrangeiros convertidos apresentam moeda original, valor original, taxa e data da cotação; item recusado por câmbio indisponível apresenta moeda original e valor original, mas omite taxa e data; estornos estrangeiros não são convertidos, têm `valor_solicitado` 0.00 e apresentam apenas moeda original e valor original entre esses campos.
**Origem:** decisões AMB-025 a AMB-029 e AMB-031 a AMB-032
**Aceite:** e-004, em moeda estrangeira e no sábado 2026-07-18, usa a cotação de 2026-07-17, tem `valor_solicitado` 178.80 e reembolso de 90.00; e-006 é RECUSADO com CAMBIO_INDISPONIVEL e `valor_solicitado` 0.00. A conversão arredonda uma única vez em BRL e sinaliza VALOR_ARREDONDADO quando necessário; valores em BRL não são convertidos.

---

## 6. Ambiguidades identificadas e decisões

> **Esta seção é o coração da spec e vale a maior parte dos 25 pontos do critério 1.**
> Uma ambiguidade que você resolveu no código sem registrar aqui conta como
> não resolvida.

### AMB-001 — Alimentação: limite de R$ 60 por dia

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia."
**O que não está claro:** é por despesa ou por dia, e como tratar vários itens no mesmo dia.
**Decisão:** o teto de R$ 60 vale para a soma de todas as refeições do mesmo dia, não para cada uma.
**Justificativa:**
**Regra afetada:** RN-008

### AMB-002 — Transporte urbano: limite de R$ 80 por dia

**Texto original do RH:** "Transporte urbano tem limite de R$ 80 por dia."
**O que não está claro:** é por corrida ou por dia, e como tratar várias corridas no mesmo dia.
**Decisão:** o teto único de R$ 80 vale para todas as corridas do dia.
**Justificativa:**
**Regra afetada:** RN-008

### AMB-003 — Hospedagem: limite de R$ 250 por diária

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."
**O que não está claro:** o que conta como diária e como ler a descrição de múltiplas noites.
**Decisão:** "diária" é uma noite. Quando a periodicidade da categoria é "diaria", o teto da despesa é o limite da política vezes o número de noites, lido da descrição. Na política v3 equivalente, o limite de hospedagem é R$ 250 por noite. Identifica-se o primeiro número inteiro maior que zero seguido de "diária", "diárias", "noite" ou "noites", com espaço opcional entre o número e a palavra, ignorando maiúsculas e acentos. Número por extenso não é reconhecido. Se não houver trecho válido, conta como 1 noite e o item recebe o alerta DIARIAS_NAO_IDENTIFICADAS.
**Aceite:** "Hotel Rio - 2 diarias" identifica 2 noites; "Airbnb 3 noites" identifica 3 noites; "Hotel 2 DIÁRIAS" identifica 2 noites; "Hospedagem" identifica 1 noite e recebe DIARIAS_NAO_IDENTIFICADAS; "2 diarias e 1 noite" identifica 2 noites.
**Justificativa:**
**Regra afetada:** RN-007 e RN-008

### AMB-004 — Despesas acima do limite são reembolsadas parcialmente

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** a empresa paga o limite e corta o excedente, ou recusa a despesa inteira.
**Decisão:** a empresa paga até o teto e corta o que passa dele. Status PARCIAL.
**Justificativa:**
**Regra afetada:** RN-008

### AMB-005 — Nota fiscal obrigatória acima de R$ 100

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** a regra vale para R$ 100,00 ou acima, e qual é o efeito da ausência de nota.
**Decisão:** despesa com valor maior que R$ 100,00 exige nota fiscal. Sem ela, o item inteiro é RECUSADO, motivo NF_AUSENTE, valor reembolsável 0 e não gasta teto. Exatamente R$ 100,00 não exige nota.
**Justificativa:**
**Regra afetada:** RN-006

### AMB-006 — Nota fiscal: por despesa ou pela soma?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** a exigência pode ser por soma de várias despesas, ou por despesa isolada.
**Decisão:** olha-se cada despesa sozinha, nunca a soma de várias.
**Justificativa:**
**Regra afetada:** RN-006

### AMB-007 — Colaborador em viagem

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** como saber que o colaborador está em viagem quando não há esse campo.
**Decisão:** a viagem é deduzida pela hospedagem. Se existe uma hospedagem não recusada nos passos anteriores à inferência de viagem da ordem de aplicação, o colaborador está em viagem do dia da despesa até esse dia mais o número de noites, inclusive; hospedagem PARCIAL também conta. O alerta VIAGEM_INFERIDA aparece apenas em item de alimentação ou transporte_urbano em BRL, em dia de viagem, com valor reembolsável maior que o teto-base.
**Justificativa:**
**Regra afetada:** RN-007

### AMB-008 — Limites ampliados em 50% na viagem

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** o aumento vale para todas as categorias ou só para algumas.
**Decisão:** na política v3 equivalente, nos dias de viagem alimentação passa de R$ 60 para R$ 90 e transporte de R$ 80 para R$ 120. Nas políticas externas, a ampliação segue o percentual definido no arquivo e aplica-se somente a alimentação e transporte_urbano; hospedagem, representação e o limiar da nota fiscal não são ampliados.
**Justificativa:**
**Regra afetada:** RN-007 e RN-008

### AMB-009 — Período de competência

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** o que acontece se a despesa ficou fora do período.
**Decisão:** vale a data da despesa. Fora do período informado, é RECUSADO, motivo FORA_COMPETENCIA.
**Justificativa:**
**Regra afetada:** RN-004

### AMB-010 — Último dia do período

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** o período inclui o primeiro e o último dia, e se a hora importa.
**Decisão:** o primeiro e o último dia do período entram. Só se compara a data, sem hora.
**Justificativa:**
**Regra afetada:** RN-004

### AMB-011 — O que é duplicata e o que o sistema faz

**Texto original do RH:** "Duplicatas devem ser tratadas."
**O que não está claro:** o que conta como duplicata e como a execução deve decidir entre os itens iguais.
**Decisão:** duas despesas são duplicatas quando têm a mesma data, categoria, fornecedor e valor. O sistema paga a primeira ocorrência pela ordem do arquivo e recusa as demais, com status RECUSADO, motivo DUPLICADA e o id da despesa mantida.
**Justificativa:**
**Regra afetada:** RN-005

### AMB-012 — Duplicata: o que entra na conta

**Texto original do RH:** "Duplicatas devem ser tratadas."
**O que não está claro:** a duplicata recusada gasta teto ou entra no resumo como item recusado.
**Decisão:** a despesa recusada como duplicata tem valor reembolsável 0, não gasta teto do dia e é contada no resumo como RECUSADO.
**Justificativa:**
**Regra afetada:** RN-005 e RN-009

### AMB-013 — Nome da categoria

**Texto original do RH:** "Categorias fora da política não são reembolsáveis."
**O que não está claro:** a empresa compara nomes com acentos, caixa e espaços, ou trata tudo como texto simples.
**Decisão:** antes de comparar, ignora-se maiúsculas, acentos e espaços nas pontas.
**Justificativa:**
**Regra afetada:** RN-001 e RN-003

### AMB-014 — Valor negativo (estorno)

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** como registrar um valor negativo e se ele deve ser tratado como despesa normal.
**Decisão:** despesa com valor negativo é um estorno: o dinheiro já está com o colaborador. O item recebe status ESTORNO e valor reembolsável 0. O estorno não altera o teto do dia e não entra em nenhum total do resumo, exceto na contagem por status.
**Justificativa:**
**Regra afetada:** RN-002 e RN-009

### AMB-015 — Valores com mais de duas casas decimais

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** como tratar valores com mais de duas casas após a vírgula.
**Decisão:** arredonda para 2 casas, meio para cima, uma única vez, ao ler a despesa. O item recebe o alerta VALOR_ARREDONDADO.
**Justificativa:**
**Regra afetada:** RN-001

### AMB-016 — Plantão e fim de semana

**Texto original do RH:** "Plantonistas e fim de semana não têm tratamento diferente."
**O que não está claro:** se o sistema deve aplicar regra especial em dias de plantão ou fim de semana.
**Decisão:** sem tratamento diferente; a despesa segue a regra da sua categoria.
**Justificativa:**
**Regra afetada:** RN-003 e RN-008

### AMB-017 — Quem perde o excedente quando o teto é do dia todo

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** se todas as despesas do dia têm o mesmo teto e quem usa primeiro perde menos.
**Decisão:** as despesas do dia são processadas por data e, em empate, pela ordem do arquivo. Cada uma recebe até o que sobrou do teto; as seguintes ficam RECUSADO, motivo LIMITE_EXCEDIDO.
**Justificativa:**
**Regra afetada:** RN-008

### AMB-018 — O que entra na soma do dia

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** o que conta para o teto do dia e o que não conta.
**Decisão:** só conta despesa elegível: categoria válida, no período, sem duplicata e com nota fiscal quando exigida. Recusadas, duplicatas e estornos não gastam teto.
**Justificativa:**
**Regra afetada:** RN-005, RN-006, RN-008 e RN-009

### AMB-019 — Política externa

**O que não está claro:** onde são definidos os limites usados no cálculo.
**Decisão:** limites e periodicidade vêm de um arquivo de política, não do código. A CLI aceita `--politica` e `--cambio` opcionais; se omitidos, usa a política e a tabela de câmbio padrão distribuídas com o projeto. Arquivo ausente, JSON inválido, limite negativo, periodicidade desconhecida ou ausência de "padrao" invalidam a entrada conforme RN-010.
**Regra afetada:** RN-010, RN-011 e RN-012

### AMB-020 — Política por centro de custo

**O que não está claro:** qual política se aplica a cada colaborador.
**Decisão:** vale a política do centro de custo do colaborador, comparado ignorando maiúsculas e espaços nas pontas. Sem centro de custo na entrada ou sem entrada correspondente na tabela, usa-se "padrao".
**Regra afetada:** RN-001 e RN-003

### AMB-021 — Herança de categoria da política padrão

**O que não está claro:** o que ocorre quando uma categoria não aparece na política do centro de custo.
**Decisão:** a categoria herda o limite da mesma categoria em "padrao". Se também não existir em "padrao", é categoria fora da política.
**Regra afetada:** RN-003

### AMB-022 — Limite zero

**O que não está claro:** se limite 0 significa pagamento de zero ou categoria não permitida.
**Decisão:** limite 0 torna a categoria não reembolsável; o item é RECUSADO com motivo CATEGORIA_FORA_POLITICA no mesmo passo da categoria fora da política.
**Regra afetada:** RN-003

### AMB-023 — Periodicidade e ampliação em viagem

**O que não está claro:** como aplicar periodicidades da política e o aumento de viagem às categorias.
**Decisão:** "dia" é teto agregado por dia; "diaria" é o limite multiplicado pelo número de noites por despesa, conforme AMB-003. Ambas valem para qualquer categoria do arquivo. A ampliação em viagem continua somente para alimentacao e transporte_urbano, usando o percentual lido do arquivo. Hospedagem, representacao e o limiar da nota fiscal não são ampliados.
**Regra afetada:** RN-007 e RN-008

### AMB-024 — Metadados da política

**O que não está claro:** se versao e vigencia do arquivo mudam o cálculo.
**Decisão:** `versao` e `vigencia` são informativos e não entram no cálculo.
**Regra afetada:** RN-012

### AMB-025 — Moeda de entrada

**O que não está claro:** qual moeda usar quando o campo não é informado e como validar seu formato.
**Decisão:** moeda é opcional; ausente significa BRL. O valor informado deve ser código de três letras ISO 4217, ignorando maiúsculas e espaços nas pontas. Formato inválido torna a entrada inválida com código 1.
**Regra afetada:** RN-001, RN-010 e RN-013

### AMB-026 — Data e disponibilidade da cotação

**O que não está claro:** qual taxa aplicar quando não há cotação no dia da despesa.
**Decisão:** usa-se a taxa da data da despesa; sem cotação nessa data, usa-se a mais recente nos cinco dias corridos anteriores. Sem taxa para a moeda ou fora dessa janela, o item é RECUSADO com motivo CAMBIO_INDISPONIVEL e `valor_solicitado` 0.00.
**Regra afetada:** RN-013

### AMB-027 — Conversão e arredondamento

**O que não está claro:** como arredondar a conversão e em qual moeda comparar tetos.
**Decisão:** valor multiplicado pela taxa é arredondado uma única vez para duas casas, meio para cima; se houve arredondamento, aplica-se o alerta VALOR_ARREDONDADO. Tetos e limiar da nota fiscal são comparados em BRL. Despesa em BRL não é convertida.
**Regra afetada:** RN-001, RN-006, RN-008 e RN-013

### AMB-028 — Moeda e valor na identificação de duplicatas

**O que não está claro:** se moeda ou diferença entre valores originais altera a identificação de duplicatas.
**Decisão:** além dos campos já definidos em AMB-011, duas despesas só são duplicatas se tiverem a mesma moeda e o mesmo valor original.
**Regra afetada:** RN-005

### AMB-029 — Valores e metadados de moeda na saída

**O que não está claro:** em qual moeda a saída e os totais são apresentados.
**Decisão:** `valor_solicitado` e `valor_reembolsavel` são sempre em BRL. Itens em moeda estrangeira trazem `moeda_original`, `valor_original`, `taxa_cambio` e `data_taxa_cambio`; estornos em moeda estrangeira não são convertidos.
**Regra afetada:** RN-002, RN-009 e RN-013

### AMB-030 — Moeda estrangeira e viagem inferida

**O que não está claro:** se uma despesa em moeda estrangeira pode gerar dias de viagem.
**Decisão:** a viagem continua inferida somente por hospedagem não recusada; despesa em moeda estrangeira não gera dia de viagem.
**Regra afetada:** RN-007

### AMB-031 — Metadados de câmbio em estorno estrangeiro

**O que não está claro:** quais metadados de conversão exibir para um estorno que não é convertido.
**Decisão:** o estorno em moeda estrangeira tem `valor_solicitado` 0.00 em BRL, apresenta `moeda_original` e `valor_original`, mas omite `taxa_cambio` e `data_taxa_cambio`.
**Regra afetada:** RN-002 e RN-013

### AMB-032 — Metadados quando o câmbio está indisponível

**O que não está claro:** quais metadados de cotação exibir quando não existe cotação aplicável.
**Decisão:** o item estrangeiro recusado por CAMBIO_INDISPONIVEL apresenta `moeda_original` e `valor_original`, mas omite `taxa_cambio` e `data_taxa_cambio`.
**Regra afetada:** RN-013

---

## 7. Casos de borda

Os casos d-001 a d-014 abaixo mantêm como referência a política equivalente à v3. Os resultados da política v4 estão especificados nos aceites do envelope após a tabela.

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| d-001 | 2026-07-03, alimentação, 72.50, com nota | Valor reembolsável 60.00 e status PARCIAL; o excedente de 12.50 é cortado | RN-008 |
| d-002 | 2026-07-03, alimentação, 38.00, com nota | Sem valor pago porque o teto do dia já foi usado | RN-008 |
| d-003 | 2026-07-06, transporte urbano, 100.00, sem nota | PARCIAL, valor reembolsável 80.00, motivo LIMITE_EXCEDIDO | RN-006 e RN-008 |
| d-004 | 2026-07-06, transporte urbano, 100.01, sem nota | RECUSADO por NF_AUSENTE, valor reembolsável 0.00 | RN-006 |
| d-005 | 2026-07-07, coworking, 89.00, com nota | RECUSADO por categoria fora da política; não gasta teto | RN-003 |
| d-006 | 2026-07-09, alimentação, 54.90, com nota | APROVADO, valor reembolsável 54.90 | RN-008 |
| d-007 | 2026-07-09, alimentação, 54.90, com nota, duplicata de d-006 | RECUSADO por DUPLICADA; mantém d-006 como original | RN-005 |
| d-008 | 2026-04-15, alimentação, 41.00, com nota | RECUSADO por FORA_COMPETENCIA | RN-004 |
| d-009 | 2026-07-11, transporte urbano, -45.00, sem nota | ESTORNO, valor reembolsável 0.00, sem impacto no teto | RN-002 |
| d-010 | 2026-07-14, hospedagem, 480.00, 2 diárias, com nota | APROVADO, teto de 500.00, sem corte; não recebe VIAGEM_INFERIDA | RN-007 e RN-008 |
| d-011 | 2026-07-15, alimentação, 33.333, com nota | APROVADO, valor_solicitado e reembolsável 33.33; recebe VALOR_ARREDONDADO, sem VIAGEM_INFERIDA porque não supera o teto-base | RN-001 e RN-007 |
| d-012 | 2026-07-18, alimentação, 47.20, com nota | APROVADO, valor reembolsável 47.20 | RN-008 |
| d-013 | 2026-07-22, hospedagem, 690.00, sem nota, 3 noites | RECUSADO por NF_AUSENTE; a ausência de nota vence antes da regra de limite | RN-006 |
| d-014 | 2026-07-31, ALIMENTACAO, 61.00, com nota | PARCIAL com valor reembolsável 60.00; o excedente de 1.00 é cortado | RN-001 e RN-008 |

**Aceites do envelope (Dia 2, política v4):**

- Em `despesas-envelope.json`, com centro de custo CC-COMERCIAL: e-001 é PARCIAL, reembolsa 300.00 e tem motivo LIMITE_EXCEDIDO; e-002 é PARCIAL, solicita 130.46 e reembolsa 90.00; e-003 é APROVADO por 85.26; e-004 é PARCIAL, solicita 178.80 e reembolsa 90.00, usando a cotação de 2026-07-17 porque a despesa ocorreu no sábado 2026-07-18; e-005 é RECUSADO por NF_AUSENTE sobre 220.00; e-006 é RECUSADO por CAMBIO_INDISPONIVEL, tem `valor_solicitado` 0.00 e apresenta apenas moeda e valor originais, sem taxa ou data de câmbio; e-007 é APROVADO por 1200.00; e-008 é APROVADO por 95.00 e recebe VIAGEM_INFERIDA; e-009 é RECUSADO por CATEGORIA_FORA_POLITICA; e-010 é APROVADO por 88.00. Os totais são 2457.52 / 1948.26 / 509.26 e a contagem é 4 aprovados, 3 parciais, 3 recusados e 0 estorno.
- Em `despesas-envelope-cc-desconhecido.json`, usando a política "padrao": f-001 é APROVADO por 58.00; f-002 é PARCIAL por 250.00; f-003 é RECUSADO por CATEGORIA_FORA_POLITICA; f-004 é APROVADO por 65.76. Os totais são 623.76 / 373.76 / 250.00 e a contagem é 2 aprovados, 1 parcial, 1 recusado e 0 estorno.
- Em `despesas-exemplo.json` com política v4 e centro de custo CC-ENG-PLATAFORMA: d-001 é APROVADO por 72.50; d-002 é PARCIAL por 2.50; d-003 é PARCIAL por 80.00; d-010 e d-013 são RECUSADOS por CATEGORIA_FORA_POLITICA; d-014 é APROVADO por 61.00; os demais itens permanecem inalterados. Os totais são 1861.84 / 351.43 / 1510.41 e a contagem é 5 aprovados, 2 parciais, 6 recusados e 1 estorno.
- Em `despesas-exemplo.json` com uma política contendo somente "padrao", equivalente à v3, o resultado da v3 permanece inalterado: totais 1861.84 / 815.43 / 1046.41 e contagem 4 aprovados, 3 parciais, 6 recusados e 1 estorno.

## 8. Ordem de aplicação das regras

1. Normalizar valor, categoria, moeda e centro de custo.
2. Separar os estornos.
3. Aplicar o câmbio.
4. Recusar categoria fora da política ou com limite 0.
5. Recusar despesas fora do período.
6. Recusar duplicatas.
7. Recusar despesas acima do limiar da nota fiscal sem nota.
8. Descobrir os dias de viagem.
9. Aplicar os tetos.
10. Calcular os totais.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] a categoria "ALIMENTACAO" é tratada como alimentação no mesmo dia em que o item entrar, sem depender de caixa ou acentos.
- [ ] d-001 e d-014 são PARCIAL, com valor reembolsável 60.00 e o excedente cortado.
- [ ] d-002, no mesmo dia da alimentação, fica RECUSADO por LIMITE_EXCEDIDO, sem gastar mais do teto do dia.
- [ ] d-006 e d-007 são tratados como duplicata; d-007 fica RECUSADO, d-006 continua como original e `despesa_mantida` de d-007 é "d-006".
- [ ] d-009 é ESTORNO, tem valor reembolsável 0.00 e não entra nos totais do resumo.
- [ ] R$ 100,00 não exige nota; d-003 é PARCIAL, com valor reembolsável 80.00 e motivo LIMITE_EXCEDIDO. d-004 e d-013 ficam RECUSADO com motivo NF_AUSENTE.
- [ ] d-010 não recebe VIAGEM_INFERIDA; d-011 recebe VALOR_ARREDONDADO, tem valor_solicitado 33.33 e não recebe VIAGEM_INFERIDA, pois seu valor reembolsável não supera o teto-base.
- [ ] d-008 é RECUSADO por FORA_COMPETENCIA, mesmo sendo uma despesa válida de outra categoria.
- [ ] no caso completo d-001 a d-014, com política equivalente à v3, o resumo informa total_solicitado 1861.84, total_reembolsavel 815.43, total_recusado 1046.41 e conta 4 aprovados, 3 parciais, 6 recusados e 1 estorno.
- [ ] os três casos do envelope v4 produzem os itens, motivos, alertas, totais e contagens definidos nos aceites desta seção; a execução do arquivo de exemplo com política somente "padrao" mantém os resultados da v3.
- [ ] `valor_solicitado` e `valor_reembolsavel` são sempre BRL; os campos de moeda original aparecem somente nos itens estrangeiros e estorno estrangeiro não é convertido.
- [ ] a CLI aceita `--politica` e `--cambio` opcionais e usa os arquivos padrão quando omitidos.
