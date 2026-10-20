# Instruções do projeto
- Fonte da verdade: specs/001-motor-reembolso/spec.md (o quê), plan.md (como), tasks.md (ordem).
- Se código e spec discordarem, o código é o bug.
- Antes de implementar, leia a task em tasks.md. Se o pedido não está em nenhuma task, avise e não implemente.
- Se eu explicar uma regra que não está na spec, pare e me diga: isso é bug de spec.
- Nunca decida uma ambiguidade sozinho: pergunte e registre em spec.md/DECISIONS.md.
- Dinheiro nunca em float (use Decimal).
- Um commit por task: feat(T-003): ... / test(T-003): ... / docs(spec): ...
- Toda regra de negócio tem teste cujo nome começa com o ID (test_rn003_...).