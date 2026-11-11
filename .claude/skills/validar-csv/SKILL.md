---
name: validar-csv
description: Valida o CSV de decisões do hackathon Fortuna antes de mandar no canal (formato, cabeçalho, maiúsculas, duas casas, duplicados, valor zero/negativo, teto de R$ 30 mil e, com o banco, ids e valor solicitado). Use quando pedirem para validar, conferir ou checar o arquivo de decisões ou o <time>_final.csv.
---

# Validar o CSV de decisões

1. Descobrir o arquivo: o que foi passado como argumento; senão procurar `*_final.csv` ou o CSV mais recente na pasta do time.
2. Rodar:

   ```bash
   python3 -I .claude/skills/validar-csv/validar.py <arquivo.csv>
   ```

   Se o banco estiver no ar (`docker exec fortuna-pg pg_isready -q`), acrescentar `--db docker` para cruzar com os 2.000 pedidos novos (ausentes, ids inexistentes, valor acima do solicitado). Não subir o banco por conta própria: se não estiver no ar, rodar sem `--db` e avisar.
3. Responder em três blocos curtos:
   - **Bloqueia a pontuação** (arquivo fora do formato: cabeçalho, separador, codificação);
   - **Perde ponto silenciosamente** (ausentes viram negado, minúscula vira negado, aprovado com 0 vira negado, valor cortado no limite);
   - **Resumo** (linhas, aprovados, negados, valor total aprovado, % aprovado).
4. Lembrar: o nome final é `<time>_final.csv` e o arquivo precisa ter sido gerado pelo código (nunca sugerir editar o CSV à mão; corrigir o código que gera).

Regras completas em `docs/06-entregaveis.md`.
