# 04 · API do bureau de crédito

Fonte: LEIA-ME §2, Manual §4.3, slide `05-api-bureau`.

- Endereço: `https://gowlab-fortuna-bureau.azurewebsites.net`
- Token: chega por mensagem privada, **só do nosso time**. Guardar em `.env` como `BUREAU_TOKEN`. Não compartilhar.
- Só serve para os pedidos **novos**. O histórico já tem bureau no banco.

## Endpoints

```
GET /v1/bureau/{id_cliente}
Authorization: Bearer <token do time>

GET /health          (sem token, testa a conexão)
```

Consulta pelo **id_cliente** do pedido novo, **não** pelo id_pedido.

```bash
set -a; source .env; set +a
curl -s "$BUREAU_URL/health"
curl -s -H "Authorization: Bearer $BUREAU_TOKEN" "$BUREAU_URL/v1/bureau/C-86419"
```

## Resposta 200 (ilustrativa)

```json
{
  "id_cliente": "C-86419",
  "score": 540,
  "restricoes_ativas": 0,
  "parcelas_outras_instituicoes": 0.00,
  "consultas_90_dias": 1,
  "meses_historico_bureau": 6
}
```

Mesmos campos e significado da tabela `bureau`.

## Status

| Status | Quando | O que fazer |
|---|---|---|
| 200 | Consulta feita | Usar os dados |
| 401 | Token ausente ou inválido | Conferir o cabeçalho `Authorization` |
| 404 | Cliente não é de pedido novo | Conferir se o id é de pedido com `tipo_base = 'novo'` |
| 503 | Bureau indisponível | Tentar de novo |

## Comportamento (de propósito)

- Parte das chamadas falha com **503** e parte **demora alguns segundos**, como num bureau real.
- **Tratar isso conta na nota de qualidade técnica.**
- A resposta de um cliente **não muda** entre chamadas → dá para cachear e rodar uma vez só.
- **Sem limite** de chamadas por minuto.
- As chamadas são **registradas por time** (a organização vê o padrão de uso).

## No workspace

- Os 2.000 clientes novos já foram consultados (sem falhas) e estão em `dados/bureau_novos.csv` e `analise.bureau_novos`.
- Nova chamada só sob pedido explícito: `python3 -I scripts/bureau.py <C-/P-...> | --faltantes | --todos` (skill `/bureau`).
- O script trata 503 e lentidão com retry e backoff (até 8 tentativas, timeout de 20 s), 16 chamadas em paralelo, e para em 401/404.
- Na primeira carga completa: ~1 min 48 s para os 2.000.
