# 01 · O desafio

Fonte: Manual §3, slides `01-cliente`, `02-politica-atual`, `03-pedido-do-cliente`.

## O cliente

**Fortuna Crédito**: fintech de crédito pessoal para quem já tem conta digital com ela.

- Teto de **R$ 30 mil** por cliente.
- Juros fixos de **3% ao mês**, parcela pela tabela Price.
- Política de aprovação com regras fixas, **parada há mais de um ano**.

## Política atual (é a referência da pontuação)

Como o manual descreve:

1. Score do bureau **> 600**.
2. Renda declarada **> R$ 2.000**.
3. **Zero** restrições ativas no bureau.
4. Parcela (Price, 3% a.m.) **≤ 30%** da renda declarada.

**Como ela se comporta de fato no histórico** (verificado em 100% dos 8.737 pedidos da política atual): as regras 1–3 decidem aprovar ou negar; a regra 4 **não nega, reduz o valor** até a parcela caber em 30% da renda.

```
aprova  = score > 600 AND renda > 2000 AND restricoes = 0
valor   = min(valor_solicitado, floor((0,30 × renda + 0,005) / fator_price × 100) / 100)
fator_price = 0,03 / (1 − 1,03^(−prazo))
```

Já implementada em `analise.v_pedidos` (`atual_aprovaria`, `atual_valor`) e em `scripts/politica_atual.sh`.

Suspeita da Fortuna: ela **nega quem pagaria bem** e **aprova quem não consegue pagar**.

## O piloto

Por seis meses um piloto com critérios mais flexíveis decidiu parte dos pedidos (`pedidos.politica_aplicada = 'piloto'`). Por isso o histórico tem aprovados que a política atual negaria — é aí que dá para medir se "negados pela atual" pagam.

## A dor

Testar política nova é manual: hipótese → planilha → simulação → aprovação. Semanas por ciclo, uma ou duas hipóteses. Padrões menos óbvios (combinações de comportamento na movimentação da conta) passam batido.

## O pedido (três coisas)

1. Mostrar os **padrões** encontrados em linguagem que o analista de risco entenda.
2. Propor uma **nova política** de aprovação **e** de cálculo do valor aprovado.
3. **Aplicar** a política aos ~2 mil pedidos novos.

## Restrição

**A IA sugere, o analista de risco decide.** Nenhuma política entra em produção sem aprovação humana. Isso precisa aparecer no pitch ("como o analista valida o que a IA propõe").
