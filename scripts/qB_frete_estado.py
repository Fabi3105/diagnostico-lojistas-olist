# -*- coding: utf-8 -*-
"""Sugestão B. Peso do frete por estado do cliente.
As correlações por estado usam a Q8 (resultados/q08_estados_populacao.csv) e a sugestão A."""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, salvar, avaliacao_recente, etapas_entrega, UF_REGIAO, ORDEM_REGIOES, RESULTADOS

d = ler("""SELECT i.order_id, i.price, i.freight_value, c.customer_state AS uf, v.seller_state AS uf_v
           FROM itens i JOIN pedidos p USING (order_id) JOIN clientes c USING (customer_id)
           JOIN vendedores v USING (seller_id) WHERE p.order_status NOT IN ('canceled', 'unavailable')""")
d["regiao"] = d.uf.map(UF_REGIAO)
d["faixa"] = pd.cut(d.price, [0, 50, 100, 200, 500, 1e9], labels=["ate50", "50-100", "100-200", "200-500", "500+"])
d["rota"] = np.where(d.uf == d.uf_v, "mesmo estado", "outro estado")
pct = lambda x: 100 * x.freight_value.sum() / x.price.sum()

# 1. por estado
s = d.groupby("uf").apply(lambda x: pd.Series({
    "itens": len(x), "preco": x.price.sum(), "frete": x.freight_value.sum(), "frete_pct": pct(x),
    "frete_med_item": x.freight_value.mean(), "preco_med_item": x.price.mean(),
    "frete_pct_50_100": pct(x[x.faixa == "50-100"]), "mesmo_uf_pct": 100 * (x.uf == x.uf_v).mean()})).sort_values("frete_pct")
q8 = pd.read_csv(os.path.join(RESULTADOS, "q08_estados_populacao.csv"), sep=";", decimal=",").set_index("uf")
tr = etapas_entrega().groupby("customer_state").et_transp.median().rename("transp_med")
s = s.join(q8[["compradores_por_100mil", "prazo_real_mediano"]]).join(tr)
salvar(s.round(2), "qB_frete_estado_1.csv")
sp = lambda a, b: round(s[a].rank().corr(s[b].rank()), 2)
print("Spearman frete 50-100 x intensidade:", sp("frete_pct_50_100", "compradores_por_100mil"),
      "| x transporte:", sp("frete_pct_50_100", "transp_med"))

# 2. por região, com frete % e mix de itens por faixa
por_faixa = lambda k: (pd.crosstab(d[k], d.faixa, values=d.freight_value, aggfunc="sum")
                       .div(pd.crosstab(d[k], d.faixa, values=d.price, aggfunc="sum")).mul(100).round(1))
x = por_faixa("regiao").loc[ORDEM_REGIOES]; x.columns = [f"frete_pct_{c}" for c in x.columns]
y = pd.crosstab(d.regiao, d.faixa, normalize="index").mul(100).round(1).loc[ORDEM_REGIOES]; y.columns = [f"pct_itens_{c}" for c in y.columns]
z = d.groupby("regiao").agg(itens=("price", "size"), frete_med_item=("freight_value", "mean"), preco_med_item=("price", "mean"),
                            preco=("price", "sum"), frete=("freight_value", "sum")).round(2)
z["pct_do_frete_total"] = (100 * z.frete / z.frete.sum()).round(1)
z["pct_do_faturamento"] = (100 * z.preco / z.preco.sum()).round(1)
salvar(z.join(x).join(y).loc[ORDEM_REGIOES], "qB_frete_estado_2.csv")

# 3. mesmo estado x outro estado
salvar(por_faixa("rota").join(d.groupby("rota").freight_value.mean().round(2).rename("frete_med_item")), "qB_frete_estado_3.csv")

# 4. nota x frete % do pedido, só pedidos entregues no prazo
o = d.groupby("order_id").agg(preco=("price", "sum"), frete=("freight_value", "sum"))
o["fp"] = 100 * o.frete / o.preco
o = o.join(avaliacao_recente().set_index("order_id").review_score).join(etapas_entrega().set_index("order_id")[["atrasado"]], how="inner")
op = o[~o.atrasado].copy()
op["fx"] = pd.cut(op.fp, [0, 10, 20, 30, 50, 1e9], labels=["ate10", "10-20", "20-30", "30-50", "50+"], include_lowest=True)
salvar(op.groupby("fx").review_score.agg(pedidos="count", nota_media="mean").round(2), "qB_frete_estado_4.csv")
print("ok: resultados/qB_frete_estado_1..4.csv")
