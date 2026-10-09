# -*- coding: utf-8 -*-
"""Roda as consultas da pasta sql/ e salva cada resultado em resultados/<nome>_<n>.csv.

As consultas foram escritas no dialeto do DuckDB. Este programa as executa:
  - no DuckDB, se o módulo estiver instalado (pip install duckdb); ou
  - no SQLite (cópia criada por base.py), traduzindo as poucas funções que mudam de dialeto:
    CAST(x AS DATE), date_diff, strftime, DATE 'aaaa-mm-dd', median e corr.
Os CSVs publicados em resultados/ foram gerados por este caminho em SQLite; conferir_relatorio.py
compara o resultado dos dois caminhos quando os dois estão disponíveis.

Uso:  python rodar_sql.py                      (todas as consultas q01..q10)
      python rodar_sql.py q01_faturamento_categoria [n]   (um arquivo; opcionalmente só a consulta n)
"""
import os, re, sys, statistics
import pandas as pd
from base import RAIZ, RESULTADOS, conexao, salvar

SQL = os.path.join(RAIZ, "sql")
ARQUIVOS = ["q01_faturamento_categoria", "q02_atraso_avaliacao", "q03_produtos_campeoes", "q03b_frete_peso",
            "q04_maiores_lojistas", "q05_cancelados", "q05b_cancelamento_ticket", "q06_cancelamento_avaliacao_atraso",
            "q07_recompra_avaliacao", "q08_estados_populacao", "q09_faturamento_mensal_anos", "q10_black_friday"]


def consultas(texto):
    sem_comentarios = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("--"))
    return [c.strip() for c in sem_comentarios.split(";") if c.strip()]


def _args(texto, ini):
    """Lê os argumentos de uma chamada de função a partir do '(' em texto[ini]; devolve (lista, fim)."""
    nivel, atual, args, i = 0, "", [], ini
    while i < len(texto):
        c = texto[i]
        if c == "(":
            nivel += 1
            if nivel > 1: atual += c
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                args.append(atual.strip()); return args, i + 1
            atual += c
        elif c == "," and nivel == 1:
            args.append(atual.strip()); atual = ""
        else:
            atual += c
        i += 1
    raise ValueError("parênteses desbalanceados")


def _troca_funcao(sql, nome, formato):
    """Substitui toda chamada nome(a, b, ...) por formato(args), respeitando parênteses aninhados."""
    padrao = re.compile(r"\b" + nome + r"\s*\(", re.I)
    pos, saida = 0, ""
    while True:
        m = padrao.search(sql, pos)
        if not m:
            return saida + sql[pos:]
        args, fim = _args(sql, m.end() - 1)
        saida += sql[pos:m.start()] + formato([traduz_sqlite(a) for a in args])
        pos = fim


def traduz_sqlite(sql):
    """DuckDB -> SQLite. Só o necessário para as consultas deste projeto."""
    s = _troca_funcao(sql, "CAST", lambda a: f"date({a[0][:-len(' AS DATE')].strip()})" if a[0].upper().endswith(" AS DATE") else f"CAST({a[0]})")
    def dd(a):
        if a[0].strip("'").lower() == "day": return f"CAST(julianday({a[2]}) - julianday({a[1]}) AS INTEGER)"
        return f"((julianday({a[2]}) - julianday({a[1]})) * 86400.0)"
    s = _troca_funcao(s, "date_diff", dd)
    s = _troca_funcao(s, "strftime", lambda a: f"strftime({a[1]}, {a[0]})" if a[1].startswith("'") else f"strftime({a[0]}, {a[1]})")
    s = re.sub(r"\b(DATE|TIMESTAMP)\s+('\d{4}-\d{2}-\d{2}[^']*')", r"\2", s)
    s = re.sub(r"read_csv_auto\('dados/externos/([^']+)'\)", r"externos_\1", s)
    return s


class Corr:
    def __init__(self): self.x, self.y = [], []
    def step(self, x, y):
        if x is not None and y is not None: self.x.append(x); self.y.append(y)
    def finalize(self):
        import statistics as st
        return st.correlation(self.x, self.y) if len(self.x) > 1 else None


class Mediana:
    def __init__(self): self.v = []
    def step(self, x):
        if x is not None: self.v.append(x)
    def finalize(self): return statistics.median(self.v) if self.v else None


def abrir():
    try:
        import duckdb
        con = duckdb.connect(os.path.join(RAIZ, "olist.duckdb"))
        if not con.sql("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'pedidos'").fetchone()[0]:
            for c in consultas(open(os.path.join(SQL, "00_carga.sql"), encoding="utf-8").read()):
                con.sql(c)
        return "duckdb", con
    except ImportError:
        con = conexao()
        con.create_aggregate("median", 1, Mediana); con.create_aggregate("corr", 2, Corr)
        ext = os.path.join(RAIZ, "dados", "externos", "populacao_uf_2017.csv")
        pd.read_csv(ext).to_sql("externos_populacao_uf_2017.csv", con, index=False, if_exists="replace")
        return "sqlite", con


def rodar(nome, so=None, motor_con=None):
    motor, con = motor_con or abrir()
    lista = consultas(open(os.path.join(SQL, nome + ".sql"), encoding="utf-8").read())
    lista = [c for c in lista if c.upper().startswith(("SELECT", "WITH"))]
    for i, sql in enumerate(lista, 1):
        if so and i != so:
            continue
        df = con.sql(sql).df() if motor == "duckdb" else pd.read_sql(traduz_sqlite(sql), con)
        arq = f"{nome}.csv" if len(lista) == 1 else f"{nome}_{i}.csv"
        salvar(df, arq, index=False)
        print(f"{arq}: {len(df)} linhas ({motor})")


if __name__ == "__main__":
    mc = abrir()
    if len(sys.argv) > 1:
        rodar(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None, mc)
    else:
        for n in ARQUIVOS:
            rodar(n, None, mc)
