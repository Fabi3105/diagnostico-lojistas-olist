# -*- coding: utf-8 -*-
"""Sugestão A. Onde nasce o atraso: aprovação, postagem do lojista ou transporte."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
from base import etapas_entrega, ler, salvar, ORDEM_REGIOES

d = etapas_entrega()
ETAPAS = ["et_aprov", "et_post", "et_transp", "total"]

def resumo(x):
    return pd.Series({"pedidos": len(x), "atraso_%": 100 * x.atrasado.mean(), "post_fora_%": 100 * x.post_fora.mean(),
                      "aprov_med": x.et_aprov.median(), "post_med": x.et_post.median(), "transp_med": x.et_transp.median(),
                      "total_med": x.total.median(), "prometido_med": x.prometido.median()})

# 1. duração das etapas: no prazo x atrasado
s = d.groupby("atrasado")[ETAPAS].agg(["median", "mean"]).round(2)
s.index = s.index.map({False: "no prazo", True: "atrasado"})
salvar(s, "qA_onde_nasce_atraso_1.csv")
m = d.groupby("atrasado")[ETAPAS].mean(); excesso = m.loc[True] - m.loc[False]
print("divisão do excesso de dias dos atrasados (%):", (100 * excesso / excesso.total).round(1).to_dict())

# 2. postagem fora do limite x atraso
x = d.groupby("post_fora").agg(pedidos=("order_id", "size"), atrasados=("atrasado", "sum"), atraso_pct=("atrasado", "mean"))
x["atraso_pct"] *= 100
x.index = x.index.map({False: "postou no limite", True: "postou fora do limite"})
salvar(x.round(2), "qA_onde_nasce_atraso_2.csv")

# 3. região do cliente; 4. mesmo estado x outro estado
salvar(d.groupby("regiao").apply(resumo).round(2).loc[ORDEM_REGIOES], "qA_onde_nasce_atraso_3.csv")
mu = d.groupby("mesmo_uf").apply(resumo).round(2); mu.index = mu.index.map({True: "mesmo estado", False: "outro estado"})
salvar(mu, "qA_onde_nasce_atraso_4.csv")

# 5. Black Friday 2017
d["periodo"] = pd.cut(d.order_purchase_timestamp, pd.to_datetime(["2017-10-01", "2017-11-20", "2017-11-27", "2018-01-01"]),
                      right=False, labels=["antes", "semana_bf", "pos_bf"])
salvar(d.dropna(subset=["periodo"]).groupby("periodo").apply(resumo).round(2), "qA_onde_nasce_atraso_5.csv")

# 6. os 5 maiores lojistas por faturamento (Q4)
top = ler("""SELECT i.seller_id, SUM(i.price) AS f FROM itens i JOIN pedidos p USING (order_id)
             WHERE p.order_status NOT IN ('canceled', 'unavailable') GROUP BY 1 ORDER BY 2 DESC LIMIT 5""")
top["lojista"] = [f"Lojista {k}" for k in range(1, 6)]
t = (d[d.seller.isin(top.seller_id)].groupby("seller").apply(resumo).round(2)
     .join(top.set_index("seller_id")).set_index("lojista").drop(columns="f").sort_index())
salvar(t, "qA_onde_nasce_atraso_6.csv")
print("ok: resultados/qA_onde_nasce_atraso_1..6.csv")
