#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p saida
docker exec -i fortuna-pg psql -v ON_ERROR_STOP=1 -U fortuna -d fortuna -q -c "\copy (
  SELECT id_pedido,
         CASE WHEN atual_aprovaria THEN 'APROVADO' ELSE 'NEGADO' END AS decisao,
         to_char(atual_valor, 'FM9999990.00') AS valor_aprovado
  FROM analise.v_pedidos
  WHERE tipo_base = 'novo'
  ORDER BY id_pedido
) TO STDOUT WITH (FORMAT csv, HEADER true)" > saida/politica_atual.csv

python3 -I .claude/skills/validar-csv/validar.py saida/politica_atual.csv --db docker
