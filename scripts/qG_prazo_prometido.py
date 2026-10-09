# -*- coding: utf-8 -*-
"""Sugestão G. Prazo prometido (vitrine) x prazo real: quanto dá para encurtar a promessa sem derrubar a nota.

Simulação: a nota esperada de cada pedido sai da curva observada "nota média x dias entre a entrega e a data
prometida". Hipótese: o cliente reagiria a um novo atraso como reagem os clientes atrasados de hoje.
Duas políticas:
  (a) corte uniforme de k dias em todas as promessas;
  (b) promessa por rota (estado do lojista -> estado do cliente) = percentil do prazo real, aprendido nos pedidos
      de 2017 e testado nos de 2018 (rotas com menos de 30 pedidos usam o estado do cliente).
Margem de erro: intervalo de 95% por reamostragem (bootstrap) dos pedidos. Não inclui a incerteza da hipótese."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import salvar, avaliacao_recente, etapas_entrega, ORDEM_REGIOES

a = etapas_entrega().merge(avaliacao_recente()[["order_id", "review_score"]], on="order_id")
a = a[a.review_score.notna()].copy()
a["real"] = (a.order_delivered_customer_date.dt.normalize() - a.order_purchase_timestamp.dt.normalize()).dt.days
a["dv"] = a.real - a.prometido                      # >0 = atrasado
curva = a.assign(dv=a.dv.clip(-30, 20)).groupby("dv").review_score.agg(nota_media="mean", pedidos="count")
salvar(curva.round(3), "qG_prazo_prometido_1.csv")
nota = lambda dv: curva.nota_media.reindex(np.clip(dv, -30, 20)).values

def ic(v, n=300):
    bs = [np.random.default_rng(i).choice(v, len(v)).mean() for i in range(n)]
    return np.percentile(bs, [2.5, 97.5])

# (a) corte uniforme
rows = []
for k in [0, 2, 4, 6, 8, 10]:
    v = nota(a.dv.values + k); lo, hi = ic(v)
    rows.append({"reducao_dias": k, "prometido_mediano": np.median(a.prometido - k), "atraso_pct": 100 * (a.dv + k > 0).mean(),
                 "nota_esperada": v.mean(), "nota_ic95_min": lo, "nota_ic95_max": hi})
salvar(pd.DataFrame(rows).round(3), "qG_prazo_prometido_2.csv", index=False)

# (b) promessa por rota, aprendida em 2017 e testada em 2018
a["rota"] = a.seller_state + ">" + a.customer_state
tr, te = a[a.order_purchase_timestamp < "2018-01-01"], a[a.order_purchase_timestamp >= "2018-01-01"].copy()
nr = tr.groupby("rota").size()
def promessa(q):
    pr, pc, pg = tr.groupby("rota").real.quantile(q), tr.groupby("customer_state").real.quantile(q), tr.real.quantile(q)
    return np.ceil(te.rota.map(pr.where(nr >= 30)).fillna(te.customer_state.map(pc)).fillna(pg))
v = nota(te.dv.values); lo, hi = ic(v)
rows = [{"politica": "atual (2018)", "prometido_mediano": te.prometido.median(), "prometido_medio": te.prometido.mean(),
         "atraso_pct": 100 * (te.dv > 0).mean(), "nota_esperada": v.mean(), "nota_ic95_min": lo, "nota_ic95_max": hi}]
for q in [0.90, 0.92, 0.93, 0.94, 0.95]:
    p = promessa(q); d = te.real - p; v = nota(d.values); lo, hi = ic(v)
    rows.append({"politica": f"por rota, percentil {int(q*100)}", "prometido_mediano": np.median(p), "prometido_medio": p.mean(),
                 "atraso_pct": 100 * (d > 0).mean(), "nota_esperada": v.mean(), "nota_ic95_min": lo, "nota_ic95_max": hi})
    te[f"p{int(q*100)}"] = p
salvar(pd.DataFrame(rows).round(3), "qG_prazo_prometido_3.csv", index=False)

# por região do cliente, política do percentil 93 (mesma nota com promessa mais curta)
def reg(x):
    return pd.Series({"pedidos": len(x), "prometido_atual": x.prometido.median(), "prometido_rota_p93": x.p93.median(),
                      "atraso_atual_pct": 100 * (x.dv > 0).mean(), "atraso_rota_p93_pct": 100 * (x.real > x.p93).mean(),
                      "nota_atual": nota(x.dv.values).mean(), "nota_rota_p93": nota((x.real - x.p93).values).mean()})
salvar(te.groupby("regiao").apply(reg).round(2).loc[ORDEM_REGIOES], "qG_prazo_prometido_4.csv")
print("ok: resultados/qG_prazo_prometido_1..4.csv; rotas com 30+ pedidos cobrem", f"{100*te.rota.isin(nr[nr>=30].index).mean():.0f}% dos pedidos de 2018")
