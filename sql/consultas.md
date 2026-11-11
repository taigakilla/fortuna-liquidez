# Consultas SQL de apoio

Conexão: `postgresql://fortuna:fortuna@127.0.0.1:55432/fortuna` (DBeaver/psql) ou `docker exec -it fortuna-pg psql -U fortuna -d fortuna`.

Quase tudo parte de **`analise.v_pedidos`** (criada por `sql/analise.sql` no `scripts/setup.sh`): uma linha por pedido, histórico e novos, com cliente, bureau unificado (histórico pelo banco, novos pela API via `analise.bureau_novos`), agregados de movimentação, parcela Price, `desfecho` e a decisão da política atual (`atual_aprovaria`, `atual_valor`).

## Colunas de analise.v_pedidos

| Grupo | Colunas |
|---|---|
| Pedido | `id_pedido`, `id_cliente`, `tipo_base`, `data_pedido`, `valor_solicitado`, `prazo_meses` |
| Histórico | `decisao`, `valor_aprovado`, `politica_aplicada`, `situacao_final`, `desfecho` (`em_dia`, `atraso`, `calote`, `aberto_em_dia`, `aberto_com_atraso`) |
| Cliente | `renda_declarada`, `profissao`, `tipo_vinculo`, `genero`, `estado_civil`, `idade`, `meses_conta`, `cep_regiao` (1º dígito do CEP) |
| Bureau | `score`, `restricoes_ativas`, `parcelas_outras_instituicoes`, `consultas_90_dias`, `meses_historico_bureau`, `tem_bureau` |
| Movimentação (12m) | `meses_mov`, `entradas_media`, `salario_medio`, `saidas_media`, `saidas_sobre_entradas`, `saldo_medio`, `pior_saldo`, `meses_saldo_negativo`, `meses_cheque_especial`, `dias_cheque_especial`, `dias_cheque_especial_3m` |
| Derivadas | `parcela_solicitada`, `comprometimento` (parcela/renda), `comprometimento_total` ((parcela + outras dívidas)/renda), `salario_sobre_renda` |
| Política atual | `atual_aprovaria`, `atual_valor` (reproduz 100% do histórico, ver `docs/09-insights.md`) |

## 1. Contagem por base e cobertura do bureau

```sql
SELECT tipo_base, count(*), count(*) FILTER (WHERE tem_bureau) AS com_bureau
FROM analise.v_pedidos GROUP BY 1;
```

## 2. Decisão real x política atual simulada

```sql
SELECT politica_aplicada, decisao, atual_aprovaria, count(*),
       count(*) FILTER (WHERE valor_aprovado = atual_valor) AS valor_igual
FROM analise.v_pedidos
WHERE tipo_base = 'historico'
GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
```

## 3. Inadimplência por safra (mostra o efeito de contratos em andamento)

```sql
SELECT date_trunc('month', data_pedido)::date AS safra,
       count(*) AS aprovados,
       round(100.0 * avg((desfecho = 'calote')::int), 1) AS pct_calote,
       round(100.0 * avg((desfecho LIKE 'aberto%')::int), 1) AS pct_em_aberto
FROM analise.v_pedidos
WHERE decisao = 'aprovado'
GROUP BY 1 ORDER BY 1;
```

## 4. Contrafactual: aprovados do piloto que a política atual negaria

```sql
SELECT atual_aprovaria, count(*) AS aprovados,
       round(100.0 * avg((desfecho = 'calote')::int), 1) AS pct_calote,
       round(100.0 * avg((desfecho LIKE '%atraso%')::int), 1) AS pct_algum_atraso
FROM analise.v_pedidos
WHERE decisao = 'aprovado' AND politica_aplicada = 'piloto'
GROUP BY 1;
```

## 5. Molde de padrão: grupo vs média (trocar a condição de `no_grupo`)

```sql
WITH base AS (
    SELECT *, (meses_cheque_especial >= 4) AS no_grupo
    FROM analise.v_pedidos
    WHERE decisao = 'aprovado'
)
SELECT round(100.0 * avg((desfecho = 'calote')::int) FILTER (WHERE no_grupo), 1) AS pct_grupo,
       round(100.0 * avg((desfecho = 'calote')::int), 1) AS pct_media,
       count(*) FILTER (WHERE no_grupo) AS clientes_grupo,
       (SELECT count(*) FROM analise.v_pedidos n
        WHERE n.tipo_base = 'novo' AND n.meses_cheque_especial >= 4) AS novos_no_grupo
FROM base;
```

## 6. Inadimplência por faixa de uma variável

```sql
SELECT width_bucket(score, 300, 900, 6) AS faixa, min(score), max(score),
       count(*) AS aprovados,
       round(100.0 * avg((desfecho = 'calote')::int), 1) AS pct_calote
FROM analise.v_pedidos
WHERE decisao = 'aprovado'
GROUP BY 1 ORDER BY 1;
```

## 7. Simulador: resultado estimado de uma política no histórico

Só dá para medir onde existe desfecho (pedidos aprovados no histórico). Trocar `nova_aprova` e `novo_valor`. Os contratos em aberto entram com uma suposição explícita (`aberto_em_dia` = +15%, `aberto_com_atraso` = +5%), que é otimista: ver `docs/09-insights.md`.

```sql
WITH pol AS (
    SELECT *,
           (atual_aprovaria AND meses_cheque_especial < 4) AS nova_aprova,
           least(valor_aprovado, atual_valor) AS novo_valor
    FROM analise.v_pedidos
    WHERE decisao = 'aprovado'
),
r AS (
    SELECT *,
           CASE desfecho WHEN 'em_dia' THEN 0.15 WHEN 'aberto_em_dia' THEN 0.15
                         WHEN 'atraso' THEN 0.05 WHEN 'aberto_com_atraso' THEN 0.05
                         WHEN 'calote' THEN -0.60 END AS taxa
    FROM pol
)
SELECT round(sum(taxa * valor_aprovado) FILTER (WHERE atual_aprovaria)) AS resultado_atual,
       round(sum(taxa * novo_valor) FILTER (WHERE nova_aprova)) AS resultado_nova,
       count(*) FILTER (WHERE atual_aprovaria) AS aprov_atual,
       count(*) FILTER (WHERE nova_aprova) AS aprov_nova
FROM r;
```

Atenção: reduzir valor no simulador não muda o desfecho, mas na pontuação real muda (aprovar menos reduz o risco). Pedidos negados no histórico não têm desfecho e ficam fora.

## 8. Pedidos novos prontos para aplicar a política

```sql
SELECT id_pedido, id_cliente, valor_solicitado, prazo_meses, renda_declarada,
       score, restricoes_ativas, comprometimento_total, meses_cheque_especial,
       atual_aprovaria, atual_valor
FROM analise.v_pedidos
WHERE tipo_base = 'novo'
ORDER BY id_pedido;
```

## 9. Explicar a decisão de um pedido (demo ao vivo no pitch)

```sql
SELECT * FROM analise.v_pedidos WHERE id_pedido = 'P-00070' \gx
```
