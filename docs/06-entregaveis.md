# 06 · Entregáveis

Fonte: Manual §5, slides `06-entregas`, `07-arquivo-decisoes`.

Três obrigatórios (painel, CSV, pitch) e um recomendado (código).

## 1. Painel de experimentação (10% da nota, mas sustenta os 25% de padrões)

Leitor: **analista de risco**. Tem que entender sem ler código. Formato livre (tela, notebook, página); a banca avalia conteúdo, não visual.

### Parte 1 — Padrões encontrados (obrigatória)

Para cada padrão:

- o que caracteriza o grupo;
- o efeito no pagamento **comparado à média**;
- quantos clientes afeta.

Formato pedido:

> Clientes com [característica] têm inadimplência de [N]%, contra [N]% da média. Afeta [N] clientes.

Um padrão só conta se o time **explicar corretamente** o que descobriu (slide `08-avaliacao`). Usar `/padrao` para revisar.

### Parte 2 — Política proposta (obrigatória)

Passos **na ordem em que são aplicados**: quando aprova, quando nega, como define o valor. Quantos passos quiser, não precisa seguir a estrutura da atual. Exemplo do manual (só formato):

1. Filtro: nega pedidos com restrição ativa no bureau.
2. Risco: um modelo treinado no histórico estima a chance de não pagar. Acima de 30%, nega.
3. Valor: risco entre 15% e 30% aprova até 60% do solicitado; abaixo de 15% aprova o solicitado.

## 2. Arquivo de decisões (CSV) — base dos 40% automáticos

Uma linha por pedido da base nova, **gerado pela solução**.

```
id_pedido,decisao,valor_aprovado
P-20431,APROVADO,8500.00
P-20432,NEGADO,0.00
```

| Item | Regra |
|---|---|
| Codificação | UTF-8 |
| Separador | vírgula |
| Decimal | ponto, duas casas (`8500.00`) |
| Cabeçalho | obrigatório, exatamente `id_pedido,decisao,valor_aprovado` |
| id_pedido | igual ao da base nova, sem repetição |
| decisao | `APROVADO` ou `NEGADO`, maiúsculas |
| valor_aprovado | > 0 quando aprovado; `0.00` quando negado |

### Como o script de pontuação trata problemas

| Situação | Tratamento |
|---|---|
| Pedido ausente | conta como negado |
| Pedido repetido | vale a primeira linha |
| id_pedido inexistente | linha ignorada |
| decisao diferente de APROVADO/NEGADO (inclusive minúscula) | conta como negado |
| Valor acima do solicitado ou de R$ 30 mil | reduzido ao limite |
| Aprovado com valor ≤ 0 | conta como negado |
| Arquivo fora do formato | **não é pontuado** |

- O slide `07-arquivo-decisoes` mostra `P-00002,NEGADO,0`, mas o manual e o dicionário pedem `0.00`. Usar sempre `0.00`.
- **Não abrir/salvar no Excel** (muda separador e número).
- Nome final: `<time>_final.csv`.
- Validar com `/validar-csv` antes de mandar; pedir também a validação oficial no canal.

## 3. Pitch (15%)

5 min com a solução **funcionando** + 2 min de perguntas. Mostrar:

- onde a IA entra no fluxo;
- os principais padrões encontrados;
- a política proposta e **o que mudou depois do checkpoint**;
- como o analista valida o que a IA propõe.

A banca pode pedir para mostrar **ao vivo** a decisão de alguns pedidos → ter um jeito rápido de consultar um `id_pedido` e explicar por que aprovou/negou e o valor.

## 4. Código (recomendado, conta em qualidade técnica)

- Zip ou link do repositório, na pasta do time, até 15h30.
- README curto com **o comando que gera o arquivo do zero**.
