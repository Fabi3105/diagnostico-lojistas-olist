# -*- coding: utf-8 -*-
"""Sugestão D. Lojistas que prejudicam a plataforma.
Critério: 30+ pedidos avaliados; taxa de nota 1 >= 1,5x a da plataforma e z >= 2 (aproximação binomial)."""
import os, warnings; warnings.filterwarnings("ignore")
from collections import Counter
import numpy as np, pandas as pd
from base import ler, salvar, avaliacao_recente, etapas_entrega, RESULTADOS

p = ler("SELECT order_id, order_status, order_delivered_customer_date, order_estimated_delivery_date FROM pedidos")
i = ler("SELECT order_id, seller_id, SUM(price) AS valor FROM itens GROUP BY 1, 2")
av = avaliacao_recente()[["order_id", "review_score"]]
a = etapas_entrega()[["order_id", "post_fora"]]
cr = pd.read_csv(os.path.join(RESULTADOS, "qC_rotulos_por_pedido.csv"), sep=";")[["order_id", "grupo"]]
d = i.merge(p, on="order_id").merge(av, on="order_id", how="left").merge(a, on="order_id", how="left").merge(cr, on="order_id", how="left")
d["efetivo"] = ~d.order_status.isin(["canceled", "unavailable"])
d["entregue"] = d.order_delivered_customer_date.notna() & (d.order_status == "delivered")
d["atrasado"] = d.entregue & (pd.to_datetime(d.order_delivered_customer_date).dt.normalize()
                              > pd.to_datetime(d.order_estimated_delivery_date).dt.normalize())
d["nota1"] = d.review_score == 1
d["c_lojista"] = d.grupo == "Lojista (separação/estoque)"
d["c_produto"] = d.grupo == "Produto"
d["fat"] = d.valor.where(d.efetivo, 0)
d["atr_ent"] = d.atrasado.where(d.entregue)

s = d.groupby("seller_id").agg(pedidos=("order_id", "size"), faturamento=("fat", "sum"), nota=("review_score", "mean"),
                               avaliados=("review_score", "count"), nota1_n=("nota1", "sum"), atraso=("atr_ent", "mean"),
                               post_fora=("post_fora", "mean"), c_lojista_n=("c_lojista", "sum"), c_produto_n=("c_produto", "sum"))
s[["atraso", "post_fora"]] = s[["atraso", "post_fora"]].astype(float)
taxa = s.nota1_n.sum() / s.avaliados.sum()
s["taxa_n1"] = s.nota1_n / s.avaliados
s["excesso"] = s.nota1_n - s.avaliados * taxa
s["z"] = s.excesso / np.sqrt(s.avaliados * taxa * (1 - taxa))
m = s[s.avaliados >= 30].copy()
m["prejudica"] = (m.taxa_n1 >= 1.5 * taxa) & (m.z >= 2)
f, o = m[m.prejudica].copy(), m[~m.prejudica]

def resumo(x):
    return pd.Series({"lojistas": len(x), "pct_pedidos": 100 * x.pedidos.sum() / s.pedidos.sum(),
                      "pct_fat": 100 * x.faturamento.sum() / s.faturamento.sum(), "pct_nota1": 100 * x.nota1_n.sum() / s.nota1_n.sum(),
                      "taxa_nota1": 100 * x.nota1_n.sum() / x.avaliados.sum(), "nota": (x.nota * x.avaliados).sum() / x.avaliados.sum(),
                      "atraso": 100 * (x.atraso * x.pedidos).sum() / x.pedidos.sum(),
                      "post_fora": 100 * (x.post_fora * x.pedidos).sum() / x.pedidos.sum(),
                      "c_lojista_por100": 100 * x.c_lojista_n.sum() / x.pedidos.sum(),
                      "c_produto_por100": 100 * x.c_produto_n.sum() / x.pedidos.sum(), "fat_med": x.faturamento.median()})
salvar(pd.DataFrame({"prejudicam": resumo(f), "demais_30+": resumo(o), "todos": resumo(s)}).round(2), "qD_lojistas_problema_1.csv")

ref_atraso = d.loc[d.entregue, "atrasado"].mean(); ref_post = d.post_fora.mean()
def causa(x):
    tags = []
    if x.post_fora >= 2 * ref_post: tags.append("postagem")
    if x.atraso >= 2 * ref_atraso: tags.append("atraso")
    if x.c_lojista_n / x.pedidos >= 0.03: tags.append("separação/estoque")
    if x.c_produto_n / x.pedidos >= 0.03: tags.append("produto")
    return " + ".join(tags) or "difuso"
f["causa"] = f.apply(causa, axis=1)
cols = ["pedidos", "avaliados", "faturamento", "nota", "taxa_n1", "excesso", "z", "atraso", "post_fora", "c_lojista_n", "c_produto_n", "causa"]
salvar(f.sort_values("faturamento", ascending=False)[cols].round(3), "qD_lojistas_problema_2.csv")
salvar(pd.Series(Counter(t for c in f.causa for t in c.split(" + "))).rename("lojistas").sort_values(ascending=False).to_frame(),
       "qD_lojistas_problema_3.csv")
print(f"ok: {len(f)} lojistas de {len(m)}; excesso de notas 1 = {f.excesso.sum():.0f}")
