# Instruções do projeto
- Fonte da verdade: specs/001-motor-reembolso/spec.md (o quê), plan.md (como), tasks.md (ordem).
- Se código e spec discordarem, o código é o bug.
- Nunca decida uma ambiguidade sozinho: pergunte e registre em spec.md/DECISIONS.md.

## Fase de documentação (editar spec.md, plan.md, tasks.md, DECISIONS.md)
- Não exige task. Edite o documento pedido, usando só o conteúdo que o usuário fornecer.
- Não escreva código nem toque em src/ ou tests/.
- Onde faltar decisão, escreva "DECISÃO PENDENTE" e avise.

## Fase de implementação (editar src/ ou tests/)
- Só implemente o que está em uma task de tasks.md. Se o pedido não está em nenhuma task, avise e pare.
- Se eu explicar uma regra que não está na spec, pare e me diga: isso é bug de spec.
- Dinheiro nunca em float (use Decimal).
- Um commit por task: feat(T-003): ... / test(T-003): ...
- Toda regra de negócio tem teste cujo nome começa com o ID (test_rn003_...).