# 09 · Números do dump e armadilhas

Números tirados direto do `kit/fortuna_hackathon.dump` (sem restaurar o banco). Visão bruta, **sem** tratar contratos em andamento. Atualizar aqui o que o time for descobrindo.

## Decisões no histórico (10.000 pedidos)

| Política | Aprovados | Negados |
|---|---|---|
| atual | 4.907 | 3.830 |
| piloto | 1.126 | 137 |
| **Total** | **6.033** | **3.967** |

## situacao_final dos aprovados

| situacao_final | atual | piloto | total |
|---|---|---|---|
| quitado_em_dia | 693 | 25 | 718 |
| quitado_com_atraso | 203 | 7 | 210 |
| em_dia | 2.768 | 675 | 3.443 |
| em_atraso | 789 | 291 | 1.080 |
| inadimplente | 454 | 128 | 582 |
| **Inadimplência bruta** | **9,3%** | **11,4%** | **9,6%** |

O piloto é mais recente (quase nada quitado), então a comparação bruta subestima o risco dele.

## Valor aprovado vs solicitado

| Política | = solicitado | < solicitado |
|---|---|---|
| atual | 4.617 | 290 |
| piloto | 1.069 | 57 |

Existem aprovações com valor reduzido nas duas políticas — dá para estudar se reduzir valor muda o desfecho.

## A política atual reproduzida (verificado no banco)

- Aprova ↔ `score > 600 AND renda > 2000 AND restricoes_ativas = 0`. Bate em **4.907/4.907** aprovados e **3.830/3.830** negados da política atual.
- A regra dos 30% **reduz o valor** em vez de negar: os 290 aprovados com valor menor que o solicitado são exatamente o maior valor cuja parcela cabe em 30% da renda (fórmula em `01-desafio.md`). Nenhum pedido foi negado só pela parcela.
- No piloto, 427 aprovados seriam negados pela atual: é o contrafactual (consulta 4 de `sql/consultas.md`).
- Nos novos pedidos, a política atual aprova **1.145 de 2.000 (57,2%)**, total **R$ 8.856.449,87** (`saida/politica_atual.csv`). É contra isso que o nosso ganho é medido.
- Bureau dos 2.000 novos já baixado em `dados/bureau_novos.csv` (sem falhas) e carregado em `analise.bureau_novos`.

## Contratos encerrados enganam

Somando só os encerrados (em dia, atraso, calote) com os pesos da pontuação, o histórico dá **−R$ 2,4 mi** em 1.510 contratos. Isso **não** quer dizer que a carteira dá prejuízo: contrato vira `inadimplente` cedo, enquanto `quitado` só aparece em contrato curto ou antigo. Os encerrados são enviesados para o calote. Comparar políticas sempre no mesmo conjunto e com a mesma suposição para os em aberto.

## Armadilhas analíticas

1. **Censura (contratos em andamento)**. 57% dos aprovados estão `em_dia` e não terminaram; muitos ainda podem virar inadimplentes. Taxa de inadimplência ingênua (inadimplente / aprovados) é **otimista**, ainda mais em safras recentes. Saídas: comparar por safra (mês do pedido), olhar só contratos com N parcelas vencidas, ou usar as `parcelas` para ver atraso precoce.
2. **Mapear situacao_final para o desfecho da pontuação** (hipótese, **confirmar com o cliente**):
   - `quitado_em_dia` → pagou em dia (+15%)
   - `quitado_com_atraso` → pagou com atraso (+5%)
   - `inadimplente` → não pagou (−60%)
   - `em_atraso` → incerto (atraso <90 dias; pode virar calote)
   - `em_dia` → incerto (provável em dia, mas em aberto)
3. **Viés de seleção**: só existe desfecho para quem foi aprovado. Os negados pela política atual só têm "contrafactual" via **piloto** — é o único lugar onde se vê como pagam clientes que a atual negaria.
4. **Desfecho depende do valor aprovado**: a pontuação diz que aprovar mais do que o cliente aguenta aumenta o calote. Política de valor (não só aprovar/negar) é alavanca.
5. **Bureau dos novos vem da API**; se a feature de bureau for usada no modelo, o time precisa ter o bureau de **todos** os 2.000 antes de gerar o CSV final.
6. **Movimentação com menos de 12 meses** = conta nova. Agregados (média, mínimo, meses com cheque especial) precisam lidar com contagem de meses variável; o próprio número de meses é uma feature.
7. **Variáveis sensíveis** (`genero`, `estado_civil`, idade, `cep`): mesmo com dados fictícios, a banca pode questionar discriminação. Ter resposta pronta se forem usadas.
8. **Comparação justa com a política atual**: para estimar ganho no histórico, simular a política atual com as mesmas regras (`sql/consultas.md`) e comparar com a proposta no mesmo conjunto.

## Ideias de padrões a testar (hipóteses, não resultados)

- Comprometimento real de renda: (parcela nova + `parcelas_outras_instituicoes`) / renda, e renda declarada vs `entradas_salario` média (renda inflada).
- Uso de cheque especial: meses com `dias_cheque_especial > 0`, tendência nos últimos 3 meses.
- Saldo: `saldo_minimo` negativo recorrente; `total_saidas / total_entradas`.
- Tempo de conta (`data_abertura_conta`) e de histórico no bureau.
- `consultas_90_dias` alto (cliente buscando crédito em vários lugares).
- Score entre 500 e 600 com boa movimentação (quem a atual nega e pagaria).
- Score > 600 com cheque especial frequente (quem a atual aprova e não paga).
- Prazo longo × valor alto.
- `tipo_vinculo` (autônomo/empresário: renda declarada menos confiável?).
