# Hackathon GOW 2026 · Desafio Fortuna Crédito · Time Liquidez

Workspace de consulta do time **Liquidez** (identificador `liquidez`, arquivo final `liquidez_final.csv`). Hoje, quarta 11/11/2026, 8h–17h. **Code freeze 15h30 sem tolerância.**

Responder em português, curto e direto, citando de onde veio (`docs/...` e seção do manual). Nunca responder regra de memória.

## Regras para o Claude neste workspace

- **Bureau só sob pedido explícito.** Os dados dos 2.000 novos já estão no banco. Chamar a API (`scripts/bureau.py`, `/bureau`) só quando alguém pedir para consultar um cliente específico ou atualizar todos. As chamadas são registradas por time.
- **`kit/` é o material original**: nunca editar. Se um doc divergir do PDF, o PDF manda; corrigir o doc.
- **O CSV de entrega tem que ser gerado por código.** Nunca editar CSV à mão nem sugerir isso (desclassifica).
- **Banco é só leitura para análise**: não alterar as tabelas de `hackathon`. Criar o que precisar no schema `analise` ou em tabela temporária.
- **Token** só no `.env`, nunca em doc, commit, chat ou Teams.
- Se o banco não responder, sugerir `scripts/setup.sh` em vez de subir algo diferente.

## Mapa

| Assunto | Arquivo |
|---|---|
| Cliente, dor, pedido, política atual (como ela age de fato), piloto | `docs/01-desafio.md` |
| Agenda e prazos | `docs/02-agenda.md` |
| Tabelas, colunas, enums, data de corte | `docs/03-dados.md` |
| API do bureau | `docs/04-api-bureau.md` |
| Taxa 3% a.m., tabela Price, limites | `docs/05-produto-parcela.md` |
| Painel, CSV, pitch, código | `docs/06-entregaveis.md` |
| Pesos e cálculo do ganho | `docs/07-avaliacao.md` |
| Regras, desclassificação, FAQ | `docs/08-regras-faq.md` |
| Números já verificados e armadilhas | `docs/09-insights.md` |
| Checklist por horário e perguntas ao cliente | `docs/10-suporte.md` |
| View de análise e consultas prontas | `sql/consultas.md`, `sql/analise.sql` |
| Material original | `kit/` (PDFs, dump, LEIA-ME, `slides/`) |

## Banco

- Container `fortuna-pg` (Postgres 16), subido e restaurado por `scripts/setup.sh`.
- Conexão: `postgresql://fortuna:fortuna@127.0.0.1:55432/fortuna` · no terminal: `docker exec -it fortuna-pg psql -U fortuna -d fortuna`.
- `hackathon.*`: tabelas originais. `analise.v_pedidos`: uma linha por pedido (histórico e novos) com cliente, bureau unificado, movimentação agregada, parcela, `desfecho` e a política atual (`atual_aprovaria`, `atual_valor`). Colunas em `sql/consultas.md`.

## Scripts

| Comando | O que faz |
|---|---|
| `scripts/setup.sh` | Sobe o banco, restaura o dump se vazio, cria `analise`, carrega o bureau dos novos |
| `python3 -I scripts/bureau.py ...` | API do bureau, **só sob pedido** (ver `/bureau`) |
| `scripts/politica_atual.sh` | Gera `saida/politica_atual.csv` (política atual nos novos) e valida |
| `python3 -I .claude/skills/validar-csv/validar.py <csv> --db docker` | Valida um CSV de decisões |

## Skills

`/regra` dúvida com fonte · `/validar-csv` confere o CSV · `/padrao` revisa um padrão do painel · `/agora` próximo marco e pendências · `/bureau` consulta a API (só manual).

## Fatos que mais caem

- Ganho = resultado da nossa política − resultado da política atual, **nos mesmos 2.000 pedidos novos**. Ganho ≤ 0 zera os 40%.
- Por aprovado: em dia **+15%**, com atraso **+5%**, não pagou **−60%** do valor aprovado. Negado = 0. O desfecho depende do valor aprovado.
- Valor aprovado ≤ solicitado e ≤ R$ 30.000. Produto: mínimo R$ 500.
- CSV: UTF-8, vírgula, cabeçalho `id_pedido,decisao,valor_aprovado`, `APROVADO`/`NEGADO`, ponto com 2 casas, negado `0.00`.
- A IA tem que participar da descoberta dos padrões **e** da decisão; IA só para escrever código não vale. Proibido dado externo ao kit.
- Bureau: histórico liga por **id_pedido** (tabela), novos por **id_cliente** (API).
