# Desafio Fortuna Crédito · Time Liquidez

Workspace de consulta do Hackathon GOW 2026, para usar com o Claude Code. Arquivo final: `liquidez_final.csv`, até **15h30**.

## Começar (2 min)

Precisa de Docker, Python 3 e Claude Code.

```bash
git clone <repo> && cd <repo>
cp .env.example .env          # colar o BUREAU_TOKEN do time (mensagem privada)
scripts/setup.sh              # sobe Postgres 16, restaura o dump e carrega o bureau dos novos
claude
```

O bureau dos 2.000 pedidos novos já vem baixado em `dados/bureau_novos.csv`, então ninguém precisa chamar a API para começar.

## Conexão do banco (DBeaver, notebook, etc.)

| Campo | Valor |
|---|---|
| Host / porta | `127.0.0.1` / `55432` |
| Banco / usuário / senha | `fortuna` / `fortuna` / `fortuna` |
| URL | `postgresql://fortuna:fortuna@127.0.0.1:55432/fortuna` |

Schemas: `hackathon` (original, só leitura) e `analise` (view `v_pedidos` pronta para análise).

## Estrutura

```
CLAUDE.md          contexto que o Claude carrega sozinho
docs/              o kit reescrito por assunto (01 a 10)
sql/               analise.sql (view) e consultas.md (consultas prontas e simulador)
scripts/           setup.sh, bureau.py, politica_atual.sh
dados/             bureau_novos.csv (cache da API)
saida/             CSVs gerados (politica_atual.csv)
kit/               material original: PDFs, dump, LEIA-ME e slides (não editar)
.claude/skills/    /regra /validar-csv /padrao /agora /bureau
```

## Atalhos no Claude

| Comando | Para quê |
|---|---|
| `/regra <dúvida>` | Resposta com a fonte (manual/dicionário) |
| `/validar-csv <arquivo>` | Confere o CSV de decisões antes de mandar |
| `/padrao <texto>` | Revisa um padrão no formato do painel |
| `/agora` | Próximo marco, tempo restante e pendências |
| `/bureau <C-/P-...> \| --faltantes \| --todos` | Consulta a API do bureau (só quando pedir) |

## Bureau

```bash
python3 -I scripts/bureau.py C-86419             # um ou mais clientes (aceita P-00000 também)
python3 -I scripts/bureau.py C-86419 --sem-salvar
python3 -I scripts/bureau.py --faltantes         # só quem falta no cache
python3 -I scripts/bureau.py --todos             # refaz os 2.000
```

Retry com backoff no 503, timeout de 20 s, cache em `dados/` e recarga no banco.

## Limpar no fim

```bash
docker compose down -v
```
