#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PSQL=(docker exec -i fortuna-pg psql -v ON_ERROR_STOP=1 -U fortuna -d fortuna)

[ -f .env ] || cp .env.example .env

docker compose up -d
until docker exec fortuna-pg pg_isready -h 127.0.0.1 -U fortuna -d fortuna -q; do sleep 1; done

tabelas=$("${PSQL[@]}" -Atc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'hackathon'")
if [ "$tabelas" = "0" ]; then
  echo "Restaurando kit/fortuna_hackathon.dump..."
  docker exec -i fortuna-pg pg_restore -U fortuna --no-owner --no-privileges -d fortuna < kit/fortuna_hackathon.dump
fi

"${PSQL[@]}" -q < sql/analise.sql

if [ -f dados/bureau_novos.csv ]; then
  "${PSQL[@]}" -q -c "TRUNCATE analise.bureau_novos" -c "\copy analise.bureau_novos FROM STDIN WITH (FORMAT csv, HEADER true)" < dados/bureau_novos.csv
fi

"${PSQL[@]}" -c "SELECT tipo_base, count(*) AS pedidos, count(*) FILTER (WHERE tem_bureau) AS com_bureau FROM analise.v_pedidos GROUP BY 1 ORDER BY 1"
echo "Pronto: postgresql://fortuna:fortuna@127.0.0.1:55432/fortuna"
