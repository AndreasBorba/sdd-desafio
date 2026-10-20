# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python | É adequada para uma CLI pequena e tem suporte direto a datas, JSON e aritmética decimal. | Go ou Node.js: seriam alternativas válidas, mas não oferecem vantagem necessária para o escopo descrito. |
| Testes | pytest | Permite organizar testes unitários, de integração e ponta a ponta, com nomes claros ligados aos requisitos. | `unittest`: já vem na biblioteca padrão, mas pytest oferece uma escrita mais concisa para os casos e verificações deste projeto. |
| CLI | argparse | É a ferramenta padrão para interpretar opções e argumentos de linha de comando. | Uma biblioteca externa de CLI: adicionaria uma dependência sem necessidade para os argumentos definidos no desafio. |
| JSON | Biblioteca JSON da biblioteca padrão | Evita dependência externa para leitura e escrita do formato de entrada e saída. | Bibliotecas JSON externas: não são necessárias para os campos definidos. |
| Aritmética monetária | `Decimal` | Representa valores monetários decimais sem os erros de aproximação de ponto flutuante e permite o arredondamento especificado. | `float`: pode introduzir erros de precisão; inteiros em centavos: exigiriam conversões próprias em cada fronteira e não correspondem diretamente à entrada decimal. |

---

## 2. Arquitetura

O fluxo separa entrada e saída do cálculo. O núcleo recebe dados já convertidos
para os tipos internos, aplica as etapas da política e retorna resultados; não
lê arquivos, não escreve arquivos e não acessa a linha de comando.

```text
linha de comando → leitura e conversão do JSON → pipeline puro de regras
                 → montagem do resultado → escrita do JSON
```

O pipeline puro executa, nesta ordem, uma função por etapa:

1. Ajustar valor e categoria.
2. Separar estornos.
3. Recusar categorias fora da política.
4. Recusar despesas fora do período.
5. Recusar duplicatas.
6. Recusar despesas acima de R$ 100,00 sem nota fiscal.
7. Identificar dias de viagem pelas hospedagens qualificadas.
8. Aplicar os tetos e decidir entre APROVADO, PARCIAL ou RECUSADO.
9. Calcular os totais e a contagem por status.

Cada função recebe dados e devolve dados, sem alterar arquivos nem manter
estado entre execuções. Um coordenador puro chama as etapas na sequência
definida pela spec. A camada externa converte JSON em tipos internos, chama o
coordenador e converte o resultado para JSON.

**Fronteiras:** leitura de argumentos, leitura e escrita de arquivos e
conversões entre JSON e tipos internos ficam fora do núcleo. As regras,
prioridade, distribuição dos tetos, alertas e totais ficam no núcleo puro.

---

## 3. Modelo de dados

- **Entrada da execução:** colaborador, período e lista ordenada de despesas,
  conforme os campos documentados na spec. A ordem original da lista é
  preservada para decidir a prioridade em caso de empate de data e duplicatas.
- **Despesa interna:** id, data, categoria normalizada, descrição, fornecedor,
  valor como `Decimal`, indicação de nota fiscal e posição original na lista.
  O valor é ajustado uma vez na etapa inicial; o valor solicitado apresentado
  no resultado é esse valor já arredondado.
- **Resultado por item:** id, valor solicitado, valor reembolsável, status,
  código do motivo, alertas e, apenas para duplicatas, id da despesa mantida.
- **Resultado da execução:** lista dos resultados na ordem da entrada e resumo
  com total solicitado, total reembolsável, total recusado e contagem por
  status, de acordo com a spec.
- **Configuração da política:** valores de tetos por categoria, percentagem de
  ampliação em viagem e limiar da nota fiscal, mantidos em um único ponto de
  configuração.

Para escrever valores `Decimal` como números JSON sem convertê-los para
`float`, a fronteira de saída terá um adaptador restrito à serialização de
decimais. Esse adaptador não decide regras nem altera valores; a saída deve
continuar usando números, conforme o schema da spec.

---

## 4. Como a política é representada

Os valores monetários e percentuais da política ficam centralizados em
`src/reembolso/configuracao.py`: tetos-base de alimentação, transporte urbano
e hospedagem, ampliação de 50% em viagem e limiar de R$ 100,00 para nota fiscal.
O código das etapas consulta essa configuração em vez de repetir números.

A identificação de categorias e seus respectivos limites também fica nesse
ponto, para manter a lista de categorias válidas junto dos tetos. O código da
política será revisto apenas quando houver uma alteração aprovada da spec.

---

## 5. Decisões técnicas

### DT-001 — Python para a aplicação

**Contexto:** o produto é uma CLI de escopo delimitado, com entrada e saída
JSON e regras que precisam de testes automatizados.
**Decisão:** usar Python.
**Alternativa descartada:** Go ou Node.js; são opções possíveis, mas não
oferecem benefício necessário para este escopo.
**Consequência:** a implementação pode aproveitar o suporte da linguagem para
datas, argumentos e estruturação em módulos; a equipe precisa ter o ambiente
Python disponível para executar o programa.

### DT-002 — Decimal para valores monetários

**Contexto:** a spec exige arredondamento monetário e cálculos exatos a duas
casas.
**Decisão:** converter valores de entrada para `Decimal` e não usar
`float` nos cálculos.
**Alternativa descartada:** `float`, por sua representação aproximada de
decimais; inteiros em centavos, por exigir conversões adicionais nas fronteiras.
**Consequência:** os cálculos mantêm precisão decimal; a leitura e escrita JSON
precisam converter números para e a partir de `Decimal` sem passar por
`float`.

### DT-003 — pytest para os testes

**Contexto:** cada regra da spec deve ter teste rastreável, além de um teste
ponta a ponta do caso completo.
**Decisão:** usar pytest para testes unitários, de integração e ponta a ponta.
**Alternativa descartada:** `unittest`, que é suficiente, mas exige mais
estrutura para os mesmos casos e verificações.
**Consequência:** os testes podem ser agrupados por regra e executados em
conjunto; pytest será uma dependência de desenvolvimento.

### DT-004 — argparse para a linha de comando

**Contexto:** a execução recebe argumentos de linha de comando para escolher
os arquivos de entrada e saída.
**Decisão:** usar `argparse` da biblioteca padrão.
**Alternativa descartada:** uma biblioteca externa de CLI, que adicionaria
dependência sem necessidade identificada.
**Consequência:** a interpretação dos argumentos permanece no adaptador de
entrada e usa recursos incluídos no Python.

### DT-005 — JSON da biblioteca padrão

**Contexto:** a interface de entrada e saída usa JSON.
**Decisão:** usar a biblioteca JSON da biblioteca padrão para ler e escrever
os documentos, com conversões explícitas de valores monetários.
**Alternativa descartada:** uma dependência externa para JSON, sem benefício
necessário para o formato descrito.
**Consequência:** a entrada pode ser convertida para `Decimal`; a saída
precisa de um adaptador de serialização para preservar decimais como números
JSON sem conversão para `float`.

### DT-006 — Núcleo puro e fronteiras de I/O

**Contexto:** mudanças de política devem ter impacto localizado e ser
verificáveis sem manipular arquivos.
**Decisão:** manter o núcleo em funções puras e separar leitura, conversão,
argumentos e escrita de arquivos.
**Alternativa descartada:** misturar cálculo, leitura e escrita em uma rotina
única, o que acoplaria regras ao formato e dificultaria testes isolados.
**Consequência:** as regras podem ser testadas sem arquivos; as fronteiras
precisam converter corretamente os dados entre JSON e os tipos internos.

### DT-007 — Uma função pura por etapa da política

**Contexto:** a ordem de aplicação afeta o resultado e está definida na spec.
**Decisão:** implementar as nove etapas na ordem documentada, com uma função
pura por passo e um coordenador que as execute sequencialmente.
**Alternativa descartada:** aplicar todas as regras em um único ciclo ou
reordená-las por conveniência, o que tornaria prioridades difíceis de verificar.
**Consequência:** a sequência fica explícita e testável; uma alteração de ordem
exige ajustar o coordenador e os testes relacionados.

### DT-008 — Configuração centralizada da política

**Contexto:** limites, ampliação e limiar da nota fiscal são valores definidos
na spec que podem mudar.
**Decisão:** manter esses valores e a associação de categorias a limites em
um único módulo de configuração.
**Alternativa descartada:** espalhar números e limites pelas funções, o que
exigiria procurar e alterar vários pontos em uma revisão de política.
**Consequência:** a configuração concentra os valores ajustáveis; alterações
nela devem permanecer alinhadas à spec e ser cobertas pelos testes de regras.

### DT-009 — Serialização decimal compatível com o schema

**Contexto:** o schema pede valores numéricos, mas o serializador JSON padrão
não escreve `Decimal` diretamente como número JSON.
**Decisão:** isolar a conversão de saída em um adaptador específico para
`Decimal`, que emita sua representação decimal como token numérico JSON sem
usar `float`.
**Alternativa descartada:** converter para `float`, por reintroduzir
aproximações; escrever como texto, por contrariar o tipo numérico do schema.
**Consequência:** os valores mantêm precisão e tipo no documento final; o
adaptador exige testes próprios para formato JSON válido e valores decimais.

### DT-010 — Estrutura de arquivos por responsabilidade

**Contexto:** o núcleo de regras e as fronteiras de I/O precisam poder mudar
independentemente.
**Decisão:** separar CLI, leitura/escrita, configuração, etapas de regras e
testes em arquivos próprios.
**Alternativa descartada:** concentrar o programa e os testes em poucos
arquivos genéricos, o que reduziria a clareza das fronteiras e da rastreabilidade.
**Consequência:** responsabilidades ficam localizadas; a estrutura inicial
tem mais arquivos do que um script único.

---

## 6. Estratégia de testes

- **Nível:** testes unitários para cada etapa e regra, testes de integração
  para a sequência do pipeline e conversões das fronteiras, e um teste de
  ponta a ponta para a CLI e os arquivos.
- **Cada `RN-NNN` da spec tem teste?** Sim. A lista de testes deve cobrir
  RN-001 a RN-009, com pelo menos um teste cujo nome começa pelo ID de cada
  regra. Uma alteração da spec deve atualizar a cobertura antes da implementação
  ser considerada concluída.
- **Casos de borda da seção 7 da spec:** cobertos por testes dos resultados de
  d-001 a d-014, incluindo status, valor reembolsável, motivo, alertas,
  referência da duplicata e efeito nos totais conforme aplicável.
- **Nomenclatura:** `test_rnNNN_<descricao>`, por exemplo
  `test_rn001_arredonda_valor_e_normaliza_categoria`. Nomes assim vinculam
  cada teste diretamente à regra correspondente.
- **Ponta a ponta:** um teste executa `exemplos/despesas-exemplo.json`, confere
  os 14 itens e valida os totais do caso completo da spec
  (`total_solicitado` 1861.84, `total_reembolsavel` 815.43,
  `total_recusado` 1046.41), além da contagem por status: 4 APROVADO,
  3 PARCIAL, 6 RECUSADO e 1 ESTORNO.
- **Serialização:** testes verificam que valores monetários são números JSON
  com duas casas decimais e que nenhuma etapa de cálculo converte valores para
  `float`.

### Estrutura de arquivos proposta

```text
src/
└── reembolso/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── entrada_saida.py
    ├── configuracao.py
    ├── modelos.py
    ├── pipeline.py
    └── regras/
        ├── __init__.py
        ├── etapa_01_normalizacao.py
        ├── etapa_02_estornos.py
        ├── etapa_03_categorias.py
        ├── etapa_04_periodo.py
        ├── etapa_05_duplicatas.py
        ├── etapa_06_nota_fiscal.py
        ├── etapa_07_viagem.py
        ├── etapa_08_tetos.py
        └── etapa_09_resumo.py
tests/
├── test_rn001_normalizacao.py
├── test_rn002_estornos.py
├── test_rn003_categorias.py
├── test_rn004_periodo.py
├── test_rn005_duplicatas.py
├── test_rn006_nota_fiscal.py
├── test_rn007_viagem.py
├── test_rn008_tetos.py
├── test_rn009_resumo.py
├── test_entrada_saida.py
└── test_ponta_a_ponta.py
```

---

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Conversão monetária inadvertida para `float` nas fronteiras JSON | Média | Manter conversores isolados e cobrir leitura, cálculo e escrita com testes de valores decimais. |
| Alteração na ordem das etapas mudar o resultado | Média | Testar a ordem do pipeline e manter testes de integração para casos com mais de uma regra aplicável. |
| Divergência entre a configuração central e a spec | Baixa | Revisar a configuração junto com cada alteração de regra e executar os testes das regras afetadas. |
| Diferença entre alerta ou motivo esperado e o resultado por item | Média | Verificar status, motivo, alertas e referência da duplicata nos testes de cada regra e no teste ponta a ponta. |

### Perguntas sobre lacunas da spec

- Como o programa deve se comportar quando o JSON de entrada estiver malformado ou não contiver um campo obrigatório: qual mensagem deve apresentar e qual código de saída deve retornar?
