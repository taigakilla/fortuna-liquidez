SET client_min_messages = warning;

CREATE SCHEMA IF NOT EXISTS analise;

CREATE TABLE IF NOT EXISTS analise.bureau_novos (
    id_cliente varchar(10) PRIMARY KEY,
    score smallint NOT NULL,
    restricoes_ativas smallint NOT NULL,
    parcelas_outras_instituicoes numeric(12,2) NOT NULL,
    consultas_90_dias smallint NOT NULL,
    meses_historico_bureau smallint NOT NULL
);

CREATE OR REPLACE VIEW analise.v_pedidos AS
WITH mov AS (
    SELECT m.id_cliente,
           count(*) AS meses_mov,
           round(avg(m.total_entradas), 2) AS entradas_media,
           round(avg(m.entradas_salario), 2) AS salario_medio,
           round(avg(m.total_saidas), 2) AS saidas_media,
           round(sum(m.total_saidas) / nullif(sum(m.total_entradas), 0), 4) AS saidas_sobre_entradas,
           round(avg(m.saldo_medio), 2) AS saldo_medio,
           min(m.saldo_minimo) AS pior_saldo,
           count(*) FILTER (WHERE m.saldo_minimo < 0) AS meses_saldo_negativo,
           count(*) FILTER (WHERE m.dias_cheque_especial > 0) AS meses_cheque_especial,
           sum(m.dias_cheque_especial) AS dias_cheque_especial,
           coalesce(sum(m.dias_cheque_especial) FILTER (
               WHERE m.mes_referencia >= date_trunc('month', p.data_pedido) - interval '3 months'), 0) AS dias_cheque_especial_3m
    FROM hackathon.movimentacao_mensal m
    JOIN hackathon.pedidos p USING (id_cliente)
    GROUP BY m.id_cliente
),
base AS (
    SELECT p.id_pedido, p.id_cliente, p.tipo_base, p.data_pedido,
           p.valor_solicitado, p.prazo_meses,
           p.decisao, p.valor_aprovado, p.politica_aplicada, p.situacao_final,
           CASE p.situacao_final
                WHEN 'quitado_em_dia'     THEN 'em_dia'
                WHEN 'quitado_com_atraso' THEN 'atraso'
                WHEN 'inadimplente'       THEN 'calote'
                WHEN 'em_atraso'          THEN 'aberto_com_atraso'
                WHEN 'em_dia'             THEN 'aberto_em_dia'
           END AS desfecho,
           c.renda_declarada, c.profissao, c.tipo_vinculo, c.genero, c.estado_civil,
           date_part('year', age(p.data_pedido, c.data_nascimento))::int AS idade,
           ((p.data_pedido - c.data_abertura_conta) / 30)::int AS meses_conta,
           left(c.cep, 1) AS cep_regiao,
           coalesce(b.score, bn.score) AS score,
           coalesce(b.restricoes_ativas, bn.restricoes_ativas) AS restricoes_ativas,
           coalesce(b.parcelas_outras_instituicoes, bn.parcelas_outras_instituicoes) AS parcelas_outras_instituicoes,
           coalesce(b.consultas_90_dias, bn.consultas_90_dias) AS consultas_90_dias,
           coalesce(b.meses_historico_bureau, bn.meses_historico_bureau) AS meses_historico_bureau,
           round(p.valor_solicitado * 0.03 / (1 - power(1.03, -p.prazo_meses)), 2) AS parcela_solicitada,
           mov.meses_mov, mov.entradas_media, mov.salario_medio, mov.saidas_media,
           mov.saidas_sobre_entradas, mov.saldo_medio, mov.pior_saldo, mov.meses_saldo_negativo,
           mov.meses_cheque_especial, mov.dias_cheque_especial, mov.dias_cheque_especial_3m
    FROM hackathon.pedidos p
    JOIN hackathon.clientes c USING (id_cliente)
    LEFT JOIN hackathon.bureau b ON b.id_pedido = p.id_pedido
    LEFT JOIN analise.bureau_novos bn ON bn.id_cliente = p.id_cliente AND p.tipo_base = 'novo'
    LEFT JOIN mov ON mov.id_cliente = p.id_cliente
)
SELECT base.*,
       score IS NOT NULL AS tem_bureau,
       round(parcela_solicitada / nullif(renda_declarada, 0), 4) AS comprometimento,
       round((parcela_solicitada + parcelas_outras_instituicoes) / nullif(renda_declarada, 0), 4) AS comprometimento_total,
       round(salario_medio / nullif(renda_declarada, 0), 4) AS salario_sobre_renda,
       CASE WHEN score IS NULL THEN NULL
            ELSE score > 600 AND renda_declarada > 2000 AND restricoes_ativas = 0
       END AS atual_aprovaria,
       CASE WHEN score > 600 AND renda_declarada > 2000 AND restricoes_ativas = 0
            THEN least(valor_solicitado, valor_max_30)
            ELSE 0
       END AS atual_valor
FROM base
CROSS JOIN LATERAL (
    SELECT floor((0.30 * renda_declarada + 0.005) / (0.03 / (1 - power(1.03, -prazo_meses))) * 100) / 100 AS valor_max_30
) v;
