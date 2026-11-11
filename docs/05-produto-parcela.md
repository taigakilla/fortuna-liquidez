# 05 · Produto, taxa e parcela

Fonte: Manual §4.5, Dicionário "Produto e parcela".

- Taxa fixa **3% ao mês**.
- Limites do produto: mínimo **R$ 500**, máximo **R$ 30.000**.
- Prazos possíveis: 6, 12, 18, 24 ou 36 meses.

## Tabela Price

```
parcela = valor × i / (1 − (1 + i)^(−n))     i = 0,03   n = prazo em meses
```

Arredondar para 2 casas **no fim** do cálculo.

| Valor | Prazo | Parcela |
|---|---|---|
| R$ 7.000 | 12 | R$ 703,23 |
| R$ 8.000 | 12 | R$ 803,70 |
| R$ 10.000 | 12 | R$ 1.004,62 |
| R$ 15.000 | 24 | R$ 885,71 |
| R$ 25.000 | 24 | R$ 1.476,19 |

SQL:

```sql
round(valor * 0.03 / (1 - power(1.03, -prazo_meses)), 2)
```

## Onde a parcela entra

- A política atual compara essa parcela com **30% da renda declarada**.
- Os **juros não entram** no resultado financeiro da pontuação: ele usa percentuais fixos sobre o valor aprovado (ver `07-avaliacao.md`).

## Valor máximo pela regra de 30% (inverso da Price)

Para uma renda `R` e prazo `n`, o maior valor que cabe em 30% é:

```
valor_max = 0,30 × R × (1 − 1,03^(−n)) / 0,03
```

Útil para políticas que reduzem o valor em vez de negar.
