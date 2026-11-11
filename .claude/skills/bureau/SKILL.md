---
name: bureau
description: Consulta a API do bureau de crédito da Fortuna para um cliente/pedido novo ou atualiza todos. Só quando o usuário pedir explicitamente.
disable-model-invocation: true
argument-hint: "<C-00000|P-00000 ...> | --faltantes | --todos"
---

# Consultar o bureau

As chamadas são registradas por time. Só rodar o que foi pedido, nunca "por garantia".

Os dados dos 2.000 clientes novos já estão em `dados/bureau_novos.csv` e no banco (`analise.bureau_novos`). Para **ver** o bureau de alguém, consultar o banco, não a API:

```sql
SELECT * FROM analise.v_pedidos WHERE id_pedido = 'P-00070';
```

Chamar a API só quando o pedido for explícito:

| Pedido | Comando |
|---|---|
| Bater no bureau do cliente/pedido X | `python3 -I scripts/bureau.py C-86419` ou `P-00070` (aceita vários) |
| Só ver a resposta, sem gravar | `python3 -I scripts/bureau.py C-86419 --sem-salvar` |
| Completar quem falta no cache | `python3 -I scripts/bureau.py --faltantes` |
| Atualizar todos os 2.000 | `python3 -I scripts/bureau.py --todos` (confirmar antes: ~2 min, 2.000+ chamadas) |

O script já trata 503 e lentidão (retry com backoff, timeout de 20 s), grava o cache e recarrega o banco. 404 = não é cliente de pedido novo. 401 = token errado no `.env`.

Argumentos recebidos: $ARGUMENTS
