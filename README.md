# Motor de reembolso

CLI em Python que calcula o reembolso de despesas corporativas a partir de um
arquivo JSON e grava os itens processados e o resumo em outro JSON.

## Executar e testar

No PowerShell, na raiz do projeto:

```powershell
$env:PYTHONPATH = "src"
python -m reembolso calcular --input exemplos/despesas-exemplo.json --output resultado.json
pytest -q
```

A CLI recebe o subcomando obrigatório `calcular`, com `--input` para o caminho
do arquivo de entrada e `--output` para o caminho do arquivo de saída. Ambos
são obrigatórios; caminhos posicionais não são aceitos. Retorna código `0` em
caso de sucesso, `1` para entrada inválida e `2` para erro de uso dos
argumentos. Em entrada inválida, a mensagem é escrita em stderr e o arquivo
de saída não é criado.

## Formato dos arquivos

A entrada contém um colaborador, o período e uma lista de despesas. Os campos
obrigatórios são `colaborador.id`, `periodo.inicio`, `periodo.fim` e, para cada
despesa, `id`, `data`, `categoria`, `fornecedor`, `valor` e `tem_nota_fiscal`.
`colaborador.nome`, `colaborador.centro_custo`, `periodo.competencia` e
`despesas[].descricao` são opcionais.

Exemplo mínimo de entrada:

```json
{
  "colaborador": {"id": "c-001"},
  "periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"},
  "despesas": [
    {
      "id": "d-001",
      "data": "2026-07-06",
      "categoria": "alimentacao",
      "fornecedor": "Restaurante",
      "valor": 42.00,
      "tem_nota_fiscal": true
    }
  ]
}
```

A saída contém `itens`, com o resultado de cada despesa (`id`,
`valor_solicitado`, `valor_reembolsavel`, `status`, `motivo` e `alertas`), e
`resumo`, com os totais e a `contagem_por_status`. Itens duplicados também
informam `despesa_mantida`.

```json
{
  "itens": [
    {
      "id": "d-001",
      "valor_solicitado": 42.00,
      "valor_reembolsavel": 42.00,
      "status": "APROVADO",
      "motivo": "",
      "alertas": []
    }
  ],
  "resumo": {
    "total_solicitado": 42.00,
    "total_reembolsavel": 42.00,
    "total_recusado": 0.00,
    "contagem_por_status": {
      "APROVADO": 1,
      "PARCIAL": 0,
      "RECUSADO": 0,
      "ESTORNO": 0
    }
  }
}
```

# Desafio Prático — Spec Driven Development

Aula bônus de SDD, fechando a trilha:

`AI Fluency` → `Claude 101` → `Claude Code 101` → `Building with the Claude API` → `Claude Code in Action` → `Módulo SDD` → **Desafio**

**Individual · 2 dias · Claude Code**

---

## Comece por aqui

1. **[`DESAFIO.md`](DESAFIO.md)** — o enunciado. Leia inteiro antes de escrever qualquer coisa.
2. **[`RUBRICA.md`](RUBRICA.md)** — como você é avaliado. É pública de propósito; leia antes de começar.
3. **[`exemplos/despesas-exemplo.json`](exemplos/despesas-exemplo.json)** — a entrada de referência. Não é decoração: percorra item por item antes de escrever a spec.
4. **[`FAQ.md`](FAQ.md)** — travou? Comece por aqui. **O instrutor está fora durante o desafio**, então o FAQ é o canal de suporte.

---

## Como participar

**1. Faça um fork deste repositório.** Ele precisa ser público, ou você não conseguirá compartilhar depois.

**2. Clone o seu fork e prepare a estrutura de trabalho:**

```bash
git clone https://github.com/<seu-usuario>/sdd-desafio.git
cd sdd-desafio
cp template/CLAUDE.md .
cp -r template/specs .
cp -r template/docs .
git add -A && git commit -m "chore: estrutura inicial a partir do template"
```

<details>
<summary>PowerShell</summary>

```powershell
git clone https://github.com/<seu-usuario>/sdd-desafio.git
cd sdd-desafio
Copy-Item template\CLAUDE.md .
Copy-Item template\specs . -Recurse
Copy-Item template\docs . -Recurse
git add -A; git commit -m "chore: estrutura inicial a partir do template"
```
</details>

Os arquivos em `template/` são esqueletos com as perguntas que cada documento precisa responder. Deixe a pasta `template/` onde está — ela serve de referência.

**3. Trabalhe no seu fork**, seguindo as três regras do jogo descritas no [`DESAFIO.md`](DESAFIO.md):

- Nenhum commit sem task
- Explicação no chat que não está na spec é bug de spec
- Interações exportadas (`/export`) e commitadas em `docs/sessions/`

**4. No Dia 2, às 10h**, você recebe uma mudança de requisito pelo canal da turma. Ela é obrigatória e vale 20 pontos. Chegue nesse momento com o sistema base funcionando e testado.

> Durante os dois dias o instrutor está de férias e não responde mensagens. Dúvida de processo: [`FAQ.md`](FAQ.md). Dúvida sobre o que a política do RH significa não tem resposta — decidir isso é o exercício.

**5. Entregue** enviando o link do seu fork no formulário. Prazo: **Dia 2, 18h**.

---

## O que o seu fork precisa conter ao final

```
seu-fork/
├── CLAUDE.md                     # convenções do projeto para o agente
├── README.md                     # como rodar e como testar o SEU projeto
├── specs/
│   └── 001-motor-reembolso/
│       ├── spec.md               # o QUÊ e o PORQUÊ
│       ├── plan.md               # o COMO
│       ├── tasks.md              # T-001..T-0NN, com critério de aceite
│       └── DECISIONS.md          # log de mudanças de spec
├── src/
├── tests/
└── docs/
    ├── sessions/                 # exports das suas conversas com o Claude
    └── RELATORIO.md              # o relatório final
```

Sobre o `README.md`: substitua este arquivo pelo README do **seu** projeto — como rodar, como testar, o que você construiu. Um README que não permite rodar o projeto custa pontos.

---

## Antes de começar, confirme que o `/export` funciona

Abra o Claude Code, troque duas mensagens, rode `/export` e confirme que o arquivo foi gerado.

Faça isso **agora**, não no Dia 2. Sem `docs/sessions/`, o critério de relatório vale zero — e já aconteceu de gente que fez tudo certo descobrir no último dia que não tinha registro nenhum do trabalho.

Exporte ao final de **cada** sessão, nomeando `docs/sessions/01-descricao-curta.md`, `02-...`, e assim por diante.

---

## O resumo em um parágrafo

Você vai receber uma política de reembolso escrita por um RH, com a redação ruim que uma política de RH real tem. Ela é ambígua em vários pontos, e você não tem acesso a ninguém para tirar dúvida. O trabalho não é implementar — é **especificar**: encontrar cada ambiguidade, decidir explicitamente, justificar e registrar. O produto funcionando vale **10 dos 100 pontos**. Os outros 90 estão na spec, na rastreabilidade `spec → tasks → commits → testes`, na resposta à mudança de requisito do Dia 2 e no relatório.

Isso é deliberado. Um projeto que roda perfeitamente com spec fraca tira nota baixa; um projeto com bug conhecido, spec impecável e trilha limpa tira nota alta.
