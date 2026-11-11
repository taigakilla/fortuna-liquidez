# 07 · Como somos avaliados

Fonte: Manual §7, slides `08-avaliacao`, `09-calculo-resultado`.

## Pesos

| Critério | Peso | Como |
|---|---|---|
| Ganho sobre a política atual | **40%** | automático, pelo CSV |
| Padrões descobertos pela IA | **25%** | banca: padrões e se a explicação está correta |
| Pitch | 15% | clareza, demo ao vivo, defesa das escolhas |
| Painel de experimentação | 10% | analista entende padrões e política sem ler código |
| Qualidade técnica | 10% | organização, tratamento de falhas do bureau, reprodutibilidade; entregar código conta a favor |

## Resultado financeiro

1. Mandamos o CSV.
2. A organização sabe o desfecho real de cada pedido novo (em dia / com atraso / não pagaria).
3. Cada aprovado gera ganho ou perda; negado = 0.
4. Soma = resultado da nossa política.
5. Mesma conta com a política atual nos mesmos pedidos.
6. **Ganho = nosso resultado − resultado da política atual.**

| Desfecho | Resultado |
|---|---|
| Pagou em dia | **+15%** do valor aprovado |
| Pagou com atraso | **+5%** |
| Não pagou | **−60%** |
| Negado | 0 |

- Percentuais líquidos (já descontam custo do dinheiro, operação e recuperação). Juros não entram.
- **Um calote apaga o lucro de quatro clientes em dia.**
- **O desfecho considera o valor aprovado**: aprovar mais do que o cliente aguenta aumenta o risco de inadimplência. Ou seja, reduzir valor pode mudar o desfecho, não só o tamanho do ganho.

### Exemplo do manual

| Pedido | Decisão | Valor | Desfecho | Resultado |
|---|---|---|---|---|
| P-001 | Aprovado | 10.000 | em dia | +1.500 |
| P-002 | Aprovado | 6.000 | com atraso | +300 |
| P-003 | Aprovado | 5.000 | não pagou | −3.000 |
| P-004 | Negado | 0 | — | 0 |
| **Total** | | | | **−1.200** |

## Ponto de equilíbrio (conta nossa, não está no manual)

Valor esperado por real aprovado:

```
E = 0,15·p_em_dia + 0,05·p_atraso − 0,60·p_calote
```

- Se ninguém atrasa: aprovar compensa enquanto **p_calote < 20%**.
- Se metade dos bons atrasa: o limite cai para ~14%.
- Como o ganho é proporcional ao valor, o mesmo risco pesa mais em pedido grande.

## Nota do critério financeiro

- Maior ganho entre os times = 10.
- Demais: `(ganho do time ÷ maior ganho) × 10`.
- Ganho **zero ou negativo = nota zero** → ser pior que a política atual zera os 40%.
- Desempate geral: maior ganho sobre a política atual.
- Premiação: 1º e 2º pela nota final.
