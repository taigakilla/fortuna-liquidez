import argparse
import re
import subprocess
import sys
from decimal import Decimal

HEADER = "id_pedido,decisao,valor_aprovado"
TETO = Decimal("30000.00")
VALOR_RE = re.compile(r"^\d+\.\d{2}$")
ID_RE = re.compile(r"^P-\d{5}$")


def carregar_novos(db):
    sql = "SELECT id_pedido || ',' || valor_solicitado FROM hackathon.pedidos WHERE tipo_base = 'novo'"
    if db == "docker":
        cmd = ["docker", "exec", "fortuna-pg", "psql", "-U", "fortuna", "-d", "fortuna", "-At", "-c", sql]
    else:
        cmd = ["psql", "-d", db, "-At", "-c", sql]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"Falha ao consultar o banco: {out.stderr.strip()}")
    return {i: Decimal(v) for i, v in (l.split(",") for l in out.stdout.split())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--db")
    args = ap.parse_args()

    bloqueia, perde, avisos = [], [], []
    raw = open(args.arquivo, "rb").read()

    if raw.startswith(b"\xef\xbb\xbf"):
        avisos.append("arquivo começa com BOM UTF-8; confirmar na validação oficial")
        raw = raw[3:]
    try:
        texto = raw.decode("utf-8")
    except UnicodeDecodeError:
        sys.exit("BLOQUEIA: arquivo não está em UTF-8")
    if "\r\n" in texto:
        avisos.append("quebras de linha CRLF (Windows)")
    if ";" in texto:
        bloqueia.append("tem ';' no arquivo: separador tem que ser vírgula")

    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != HEADER:
        bloqueia.append(f"cabeçalho tem que ser exatamente '{HEADER}', veio '{linhas[0] if linhas else ''}'")

    vistos, aprovados, negados, total = set(), 0, 0, Decimal("0")
    decisoes = {}
    for n, linha in enumerate(linhas[1:], start=2):
        if not linha.strip():
            avisos.append(f"linha {n} vazia")
            continue
        partes = linha.split(",")
        if len(partes) != 3:
            bloqueia.append(f"linha {n}: {len(partes)} colunas: {linha!r}")
            continue
        idp, dec, val = (p.strip() for p in partes)
        if partes[0] != idp or partes[1] != dec or partes[2] != val:
            avisos.append(f"linha {n}: espaços em volta dos campos")
        if not ID_RE.match(idp):
            perde.append(f"linha {n}: id_pedido fora do padrão P-00000: {idp!r}")
        if idp in vistos:
            perde.append(f"linha {n}: {idp} repetido (vale só a primeira linha)")
            continue
        vistos.add(idp)
        if not VALOR_RE.match(val):
            if dec == "NEGADO" and re.fullmatch(r"0(\.0*)?", val):
                avisos.append(f"linha {n}: NEGADO com {val!r}; o manual pede 0.00 (o slide mostra 0)")
                negados += 1
                continue
            bloqueia.append(f"linha {n}: valor {val!r} tem que ter ponto e duas casas (ex.: 8500.00)")
            continue
        valor = Decimal(val)
        if dec == "APROVADO":
            if valor <= 0:
                perde.append(f"linha {n}: {idp} APROVADO com valor {val} (conta como negado)")
                continue
            if valor > TETO:
                perde.append(f"linha {n}: {idp} acima de R$ 30 mil ({val}), será cortado")
            aprovados += 1
            total += min(valor, TETO)
            decisoes[idp] = valor
        elif dec == "NEGADO":
            if valor != 0:
                perde.append(f"linha {n}: {idp} NEGADO com valor {val} (tem que ser 0.00)")
            negados += 1
        else:
            perde.append(f"linha {n}: decisao {dec!r} inválida (conta como negado; só APROVADO/NEGADO)")

    if args.db:
        novos = carregar_novos(args.db)
        ausentes = set(novos) - vistos
        extras = vistos - set(novos)
        if ausentes:
            perde.append(f"{len(ausentes)} pedidos novos ausentes (contam como negado), ex.: {sorted(ausentes)[:5]}")
        if extras:
            perde.append(f"{len(extras)} id_pedido que não existem na base nova (ignorados), ex.: {sorted(extras)[:5]}")
        acima = [i for i, v in decisoes.items() if i in novos and v > novos[i]]
        if acima:
            perde.append(f"{len(acima)} aprovados acima do valor solicitado (serão cortados), ex.: {acima[:5]}")
    else:
        avisos.append("sem --db: não conferi ids ausentes/extras nem valor acima do solicitado")

    print("== BLOQUEIA A PONTUAÇÃO ==")
    print("\n".join(f"- {x}" for x in bloqueia[:30]) or "- nada")
    print("== PERDE PONTO ==")
    print("\n".join(f"- {x}" for x in perde[:30]) or "- nada")
    if len(perde) > 30:
        print(f"- ... e mais {len(perde) - 30}")
    print("== AVISOS ==")
    print("\n".join(f"- {x}" for x in avisos) or "- nada")
    linhas_dados = aprovados + negados
    print("== RESUMO ==")
    print(f"- linhas válidas: {linhas_dados} (esperado 2000)")
    print(f"- aprovados: {aprovados} ({100 * aprovados / linhas_dados:.1f}%)" if linhas_dados else "- aprovados: 0")
    print(f"- negados: {negados}")
    print(f"- valor total aprovado: R$ {total:,.2f}")
    sys.exit(1 if bloqueia else 0)


if __name__ == "__main__":
    main()
