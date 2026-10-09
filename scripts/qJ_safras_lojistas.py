# -*- coding: utf-8 -*-
"""Análise J (revisão final). Retenção dos lojistas por safra de entrada e curva de sobrevivência.

Safra = trimestre da primeira venda efetiva. "Ativo após k meses" = teve ao menos uma venda efetiva k meses ou mais
depois da primeira (k = 3, 6, 9, 12). Só entram, em cada k, as safras que tiveram k meses completos de observação
antes de 01/09/2018 (sem isso, as safras recentes pareceriam piores só por falta de tempo).
Como a base é amostra, um lojista pequeno pode "sumir" por acaso; a curva compara safras entre si, com o mesmo viés."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, salvar

REF = pd.Timestamp("2018-09-01")
d = ler("""SELECT DISTINCT i.seller_id, p.order_purchase_timestamp AS ts FROM itens i JOIN pedidos p USING (order_id)
           WHERE p.order_status NOT IN ('canceled', 'unavailable')""")
d["ts"] = pd.to_datetime(d.ts); d = d[d.ts < REF]
g = d.groupby("seller_id").ts.agg(primeira="min", ultima="max")
g["safra"] = g.primeira.dt.to_period("Q").astype(str)
g["meses_ativo"] = (g.ultima - g.primeira).dt.days / 30.44
g["meses_observados"] = (REF - g.primeira).dt.days / 30.44
linhas = []
for safra, x in g[g.primeira >= "2017-01-01"].groupby("safra"):
    r = {"safra": safra, "lojistas": len(x)}
    for k in [3, 6, 9, 12]:
        r[f"ativos_apos_{k}m_pct"] = round(100 * (x.meses_ativo >= k).mean(), 1) if (x.meses_observados >= k).all() else np.nan
    linhas.append(r)
t1 = pd.DataFrame(linhas)
tot = {"safra": "todas (com observação completa)", "lojistas": int(t1.lojistas.sum())}
for k in [3, 6, 9, 12]:
    x = g[(g.primeira >= "2017-01-01") & (g.meses_observados >= k)]
    tot[f"ativos_apos_{k}m_pct"] = round(100 * (x.meses_ativo >= k).mean(), 1)
t1 = pd.concat([t1, pd.DataFrame([tot])], ignore_index=True)
salvar(t1, "qJ_safras_lojistas_1.csv", index=False)

# curva de sobrevivência mês a mês (todas as safras com observação completa em cada mês), separada por vendas nos 90 dias iniciais
e = d.join(g.primeira, on="seller_id"); e = e[(e.ts - e.primeira).dt.days < 90]
g["ped90"] = e.groupby("seller_id").ts.size().reindex(g.index).fillna(0)
g["grupo"] = np.where(g.ped90 >= 5, "5+ vendas nos primeiros 90 dias", "até 4 vendas nos primeiros 90 dias")
linhas = []
for k in range(0, 19):
    x = g[(g.primeira >= "2017-01-01") & (g.meses_observados >= k)]
    r = {"meses_desde_a_primeira_venda": k, "lojistas_observados": len(x), "ativos_pct": round(100 * (x.meses_ativo >= k).mean(), 1)}
    for grp, y in x.groupby("grupo"): r[grp] = round(100 * (y.meses_ativo >= k).mean(), 1)
    linhas.append(r)
t2 = pd.DataFrame(linhas); salvar(t2, "qJ_safras_lojistas_2.csv", index=False)
print(t1.to_string()); print(t2.to_string())
