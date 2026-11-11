# 03 · Dados

Fonte: Dicionário de dados (`kit/Dicionario de dados.pdf`), Manual §4, DDL tirado do dump.

## Visão geral

PostgreSQL 16, schema `hackathon`, cinco tabelas.

| Tabela | Uma linha por | Base | Linhas no dump |
|---|---|---|---|
| `clientes` | cliente | histórica e novos | 12.000 |
| `pedidos` | pedido de crédito | histórica e novos | 12.000 (10.000 historico + 2.000 novo) |
| `movimentacao_mensal` | cliente × mês | histórica e novos | 132.156 |
| `bureau` | pedido | **só histórica** | 10.000 |
| `parcelas` | parcela de pedido aprovado | **só histórica** | 135.792 |

- Histórico: pedidos de **out/2024 a set/2026**, com decisão, valor aprovado e pagamentos.
- Novos: **2.000 pedidos de out/2026**, sem decisão e sem desfecho; bureau vem da API.
- **Cada cliente aparece em um único pedido** (cliente ↔ pedido é 1:1).
- Dinheiro: `NUMERIC(12,2)`. Datas: `DATE`, sem hora.

## Data de corte: 30/09/2026

- Nenhum pagamento depois de 30/09/2026.
- Parcela que vence depois do corte: sem `data_pagamento` e sem `dias_atraso`.
- Parte dos contratos está em andamento (um contrato de ago/2026 tem uma ou duas parcelas vencidas).

## Relacionamentos

```
clientes (id_cliente) 1──1 pedidos (id_pedido) 1──1 bureau (id_pedido)         [só historico]
clientes (id_cliente) 1──N movimentacao_mensal (id_cliente, mes_referencia)
pedidos  (id_pedido)  1──N parcelas (id_pedido, numero_parcela)                [só historico aprovado]
```

Atenção: `bureau` liga por **id_pedido**; a API dos novos consulta por **id_cliente**.

## clientes — cadastro na data do pedido

| Coluna | Tipo | Valores / exemplo |
|---|---|---|
| `id_cliente` | VARCHAR(10) PK | `C-69101` |
| `renda_declarada` | NUMERIC(12,2) | renda mensal informada, `2350.00` |
| `profissao` | VARCHAR(60) | `Auxiliar administrativo` |
| `tipo_vinculo` | VARCHAR(20) | `assalariado`, `autonomo`, `empresario`, `aposentado` |
| `data_abertura_conta` | DATE | `2022-01-19` |
| `genero` | VARCHAR(20) | `feminino`, `masculino`, `nao_informado` |
| `data_nascimento` | DATE | `1980-06-09` |
| `estado_civil` | VARCHAR(20) | `solteiro`, `casado`, `uniao_estavel`, `divorciado`, `viuvo` |
| `cep` | CHAR(9) | `40868-350` |

## pedidos

| Coluna | Tipo | Valores / exemplo |
|---|---|---|
| `id_pedido` | VARCHAR(10) PK | `P-00014` |
| `id_cliente` | VARCHAR(10) FK | `C-69101` |
| `data_pedido` | DATE | `2026-08-09` |
| `valor_solicitado` | NUMERIC(12,2) | `2700.00` |
| `prazo_meses` | SMALLINT | `6`, `12`, `18`, `24`, `36` |
| `tipo_base` | VARCHAR(10) | `historico`, `novo` |
| `decisao` | VARCHAR(10) | `aprovado`, `negado`; vazio nos novos |
| `valor_aprovado` | NUMERIC(12,2) | vazio nos negados e nos novos |
| `politica_aplicada` | VARCHAR(10) | `atual`, `piloto`; vazio nos novos |
| `situacao_final` | VARCHAR(20) | só nos históricos aprovados (abaixo) |

### situacao_final

| Valor | Significado |
|---|---|
| `quitado_em_dia` | Encerrado, todas pagas, nenhuma com atraso |
| `quitado_com_atraso` | Encerrado, todas pagas, ao menos uma com atraso |
| `em_dia` | Em andamento, sem nenhum atraso até o corte |
| `em_atraso` | Em andamento com algum atraso (paga com atraso, ou vencida e não paga há < 90 dias) |
| `inadimplente` | Alguma parcela vencida e não paga há **≥ 90 dias** no corte |

"Em andamento" = tem parcela a vencer, ou vencida e não paga há menos de 90 dias.

## movimentacao_mensal — 12 meses antes do mês do pedido

Pedido de 09/08/2026 → movimentação de ago/2025 a jul/2026. Conta mais nova tem menos meses (só os meses em que a conta existia).

| Coluna | Tipo | Exemplo |
|---|---|---|
| `id_cliente` | VARCHAR(10), PK com `mes_referencia` | `C-69101` |
| `mes_referencia` | DATE, sempre dia 1 | `2026-07-01` |
| `total_entradas` | NUMERIC(12,2) | `2151.49` |
| `entradas_salario` | NUMERIC(12,2) | parte das entradas identificada como salário, `2037.03` |
| `total_saidas` | NUMERIC(12,2) | `849.24` |
| `saldo_medio` | NUMERIC(12,2) | `17344.18` |
| `saldo_minimo` | NUMERIC(12,2) | negativo = entrou no cheque especial |
| `dias_cheque_especial` | SMALLINT | dias com saldo negativo no mês |

## bureau — consulta na data do pedido (só histórica)

| Coluna | Tipo | Exemplo |
|---|---|---|
| `id_pedido` | VARCHAR(10) PK FK | `P-00014` |
| `score` | SMALLINT, 0–1000 | `832` |
| `restricoes_ativas` | SMALLINT | `0` |
| `parcelas_outras_instituicoes` | NUMERIC(12,2) | valor mensal pago em outras dívidas |
| `consultas_90_dias` | SMALLINT | consultas ao CPF nos últimos 90 dias |
| `meses_historico_bureau` | SMALLINT | `149` |

## parcelas — todas as parcelas dos aprovados históricos

Inclui as que vencem depois do corte.

| Coluna | Tipo | Observação |
|---|---|---|
| `id_pedido` | VARCHAR(10), PK com `numero_parcela` | |
| `numero_parcela` | SMALLINT | a partir de 1 |
| `data_vencimento` | DATE | mesmo dia do pedido nos meses seguintes (29–31 viram 28) |
| `valor_parcela` | NUMERIC(12,2) | |
| `data_pagamento` | DATE | vazio se não paga até o corte (atraso ou ainda não venceu) |
| `dias_atraso` | SMALLINT | paga: dias entre vencimento e pagamento (0 se no prazo); vencida não paga: atraso acumulado até o corte; a vencer: vazio |

| Situação | Exemplo | data_pagamento | dias_atraso |
|---|---|---|---|
| Paga | P-00014 parc. 1, venceu 09/09/2026 | 2026-09-09 | 0 |
| A vencer | P-00014 parc. 2, vence 09/10/2026 | vazio | vazio |
| Vencida e não paga | P-00073 parc. 4, venceu 18/11/2025 | vazio | 316 |

## Restauração

`scripts/setup.sh` faz tudo: sobe o container `fortuna-pg` (Postgres 16, porta 55432), restaura `kit/fortuna_hackathon.dump` se o banco estiver vazio, cria o schema `analise` e carrega o bureau dos novos. Conferência esperada: `historico = 10000`, `novo = 2000`, todos com bureau.

## Constraints relevantes (do DDL)

- `bureau.score` entre 0 e 1000.
- `clientes.cep` no formato `^[0-9]{5}-[0-9]{3}$`.
- `pedidos.prazo_meses` ∈ {6, 12, 18, 24, 36}.
- `movimentacao_mensal.mes_referencia` sempre dia 1.
- Todos os campos de `clientes`, `bureau` e `movimentacao_mensal` são `NOT NULL`.
