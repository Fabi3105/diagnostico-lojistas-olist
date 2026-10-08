# -*- coding: utf-8 -*-
"""
Roda um arquivo .sql no DuckDB e mostra o resultado de cada consulta.
Uso:  py rodar_sql.py sql\01_exploracao.sql
      py rodar_sql.py sql\01_exploracao.sql 3     (roda só a 3ª consulta do arquivo)

- As tabelas são criadas por sql\00_carga.sql e ficam salvas em olist.duckdb.
- As consultas são separadas por ponto e vírgula; linhas que começam com -- são comentários.
"""
import os, sys, time
import duckdb

RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(RAIZ)                                   # caminhos dos CSV relativos à pasta do projeto


def consultas(texto):
    sem_comentarios = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("--"))
    return [c.strip() for c in sem_comentarios.split(";") if c.strip()]


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: py rodar_sql.py sql\\arquivo.sql [número da consulta]")
    arq = sys.argv[1]
    lista = consultas(open(arq, encoding="utf-8").read())
    so = int(sys.argv[2]) if len(sys.argv) > 2 else None
    con = duckdb.connect(os.path.join(RAIZ, "olist.duckdb"))
    for i, sql in enumerate(lista, 1):
        if so and i != so:
            continue
        print(f"\n=== Consulta {i} " + "=" * 50)
        print(sql if len(sql) < 400 else sql[:400] + " ...")
        inicio = time.time()
        try:
            r = con.sql(sql)
            if r is not None:
                try:
                    r.show(max_rows=40, max_width=160)
                except TypeError:                # versões antigas do DuckDB
                    r.show()
            print(f"({time.time() - inicio:.2f} s)")
        except Exception as e:
            print("ERRO:", e)
    con.close()


if __name__ == "__main__":
    main()
