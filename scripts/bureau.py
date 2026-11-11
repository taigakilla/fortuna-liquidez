import argparse
import csv
import json
import os
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "dados" / "bureau_novos.csv"
CAMPOS = ["id_cliente", "score", "restricoes_ativas", "parcelas_outras_instituicoes", "consultas_90_dias", "meses_historico_bureau"]
TENTATIVAS = 8
TIMEOUT = 20
THREADS = 16


def carregar_env():
    env = RAIZ / ".env"
    if env.exists():
        for linha in env.read_text().splitlines():
            if "=" in linha and not linha.startswith("#"):
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    url = os.environ.get("BUREAU_URL", "").rstrip("/")
    token = os.environ.get("BUREAU_TOKEN", "")
    if not url or not token:
        sys.exit("Preencha BUREAU_URL e BUREAU_TOKEN no .env")
    return url, token


def psql(sql):
    out = subprocess.run(
        ["docker", "exec", "fortuna-pg", "psql", "-U", "fortuna", "-d", "fortuna", "-Atc", sql],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.split()


def resolver_cliente(ident):
    if ident.startswith("P-"):
        achados = psql(f"SELECT id_cliente FROM hackathon.pedidos WHERE id_pedido = '{ident}'")
        if not achados:
            sys.exit(f"{ident} não existe")
        return achados[0]
    return ident


def consultar(url, token, id_cliente):
    req = urllib.request.Request(f"{url}/v1/bureau/{id_cliente}", headers={"Authorization": f"Bearer {token}"})
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (401, 404):
                raise RuntimeError(f"{id_cliente}: HTTP {e.code}") from e
            motivo = f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            motivo = type(e).__name__
        time.sleep(min(2 ** tentativa, 30) * random.uniform(0.5, 1.0))
    raise RuntimeError(f"{id_cliente}: falhou {TENTATIVAS}x ({motivo})")


def ler_cache():
    if not CACHE.exists():
        return {}
    with CACHE.open() as f:
        return {r["id_cliente"]: r for r in csv.DictReader(f)}


def gravar_cache(dados):
    CACHE.parent.mkdir(exist_ok=True)
    with CACHE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for c in sorted(dados):
            w.writerow(dados[c])


def recarregar_banco():
    subprocess.run([str(RAIZ / "scripts" / "setup.sh")], check=True, stdout=subprocess.DEVNULL)


def buscar_lote(url, token, clientes):
    resultados, falhas = {}, []
    with ThreadPoolExecutor(THREADS) as pool:
        futuros = {pool.submit(consultar, url, token, c): c for c in clientes}
        for n, fut in enumerate(as_completed(futuros), start=1):
            try:
                r = fut.result()
                resultados[r["id_cliente"]] = {k: r[k] for k in CAMPOS}
            except RuntimeError as e:
                falhas.append(str(e))
            if n % 100 == 0:
                print(f"  {n}/{len(clientes)}")
    return resultados, falhas


def main():
    ap = argparse.ArgumentParser(
        description="Consulta a API do bureau. Só rodar quando alguém pedir: as chamadas são registradas por time.",
    )
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("ids", nargs="*", default=[], help="id_cliente (C-00000) ou id_pedido (P-00000) a consultar")
    grupo.add_argument("--faltantes", action="store_true", help="consulta só os clientes novos que ainda não estão no cache")
    grupo.add_argument("--todos", action="store_true", help="consulta de novo os 2.000 clientes novos e sobrescreve o cache")
    ap.add_argument("--sem-salvar", action="store_true", help="só mostra a resposta, não grava no cache nem no banco")
    args = ap.parse_args()
    if not (args.ids or args.faltantes or args.todos):
        ap.error("informe ids, --faltantes ou --todos")

    url, token = carregar_env()
    cache = ler_cache()

    if args.ids:
        clientes = [resolver_cliente(i) for i in args.ids]
    else:
        novos = psql("SELECT id_cliente FROM hackathon.pedidos WHERE tipo_base = 'novo' ORDER BY id_cliente")
        clientes = novos if args.todos else [c for c in novos if c not in cache]
        print(f"A consultar: {len(clientes)} clientes")

    resultados, falhas = buscar_lote(url, token, clientes)

    if args.ids:
        for c in clientes:
            if c in resultados:
                antes = cache.get(c)
                mudou = antes is not None and {k: str(v) for k, v in resultados[c].items()} != {k: str(v) for k, v in antes.items()}
                print(json.dumps(resultados[c], ensure_ascii=False) + ("  (diferente do cache)" if mudou else ""))

    if resultados and not args.sem_salvar:
        cache.update(resultados)
        gravar_cache(cache)
        recarregar_banco()
        print(f"Cache {CACHE.relative_to(RAIZ)}: {len(cache)} clientes · banco recarregado")

    if falhas:
        print(f"{len(falhas)} falhas:")
        print("\n".join(f"  {x}" for x in falhas[:20]))
        sys.exit(1)


if __name__ == "__main__":
    main()
