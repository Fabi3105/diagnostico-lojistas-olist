# -*- coding: utf-8 -*-
"""Sugestão C. Cruzamento dos temas das notas 1 (classificados com IA) com os pedidos.

A classificação foi feita por agentes do Claude seguindo metodo/qC_instrucoes_classificacao_ia.md; o resultado
(só ids e rótulos) está em resultados/qC_rotulos_por_pedido.csv. Este script refaz os cruzamentos."""
import os, warnings; warnings.filterwarnings("ignore")
import pandas as pd
from base import ler, salvar, etapas_entrega, UF_REGIAO, ORDEM_REGIOES, RESULTADOS

r = pd.read_csv(os.path.join(RESULTADOS, "qC_rotulos_por_pedido.csv"), sep=";")
p = ler("SELECT * FROM pedidos")
for c in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]:
    p[c] = pd.to_datetime(p[c])
av = ler("SELECT order_id, review_score, review_creation_date, review_answer_timestamp FROM avaliacoes")
av = av.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")
av["review_creation_date"] = pd.to_datetime(av.review_creation_date)
it = ler("SELECT order_id, COUNT(*) AS n_itens, COUNT(DISTINCT seller_id) AS n_lojistas, SUM(price) AS valor FROM itens GROUP BY 1")
cl = ler("SELECT customer_id, customer_state FROM clientes")
d = (r.merge(p, on="order_id", how="left").merge(av[["order_id", "review_creation_date"]], on="order_id", how="left")
      .merge(it, on="order_id", how="left").merge(cl, on="customer_id", how="left"))
d["entregue"] = d.order_delivered_customer_date.notna()
d["atrasado"] = d.entregue & (d.order_delivered_customer_date.dt.normalize() > d.order_estimated_delivery_date.dt.normalize())
d["aval_antes_entrega"] = (~d.entregue) | (d.review_creation_date < d.order_delivered_customer_date.dt.normalize())
d["regiao"] = d.customer_state.map(UF_REGIAO)

# 1. por tema
t = d.groupby("tema").agg(comentarios=("cid", "size"), sem_resposta_pct=("sem_resposta", "mean"), entregue_pct=("entregue", "mean"),
                          atrasado_pct=("atrasado", "mean"), aval_antes_entrega_pct=("aval_antes_entrega", "mean"),
                          multi_item_pct=("n_itens", lambda x: (x > 1).mean()), multi_lojista_pct=("n_lojistas", lambda x: (x > 1).mean()),
                          ticket_med=("valor", "median"))
t["pct"] = t.comentarios / len(d)
for k in [c for c in t.columns if c.endswith("pct")]:
    t[k] = (100 * t[k]).round(1)
t["grupo"] = t.index.map(d.drop_duplicates("tema").set_index("tema").grupo)
salvar(t.sort_values("comentarios", ascending=False), "qC_comentarios_nota1_1.csv")

# 2. por grupo; 3. grupo por região
g = d.groupby("grupo").agg(comentarios=("cid", "size"), sem_resposta=("sem_resposta", "mean"))
g["pct"] = (100 * g.comentarios / len(d)).round(1)
salvar(g.sort_values("comentarios", ascending=False), "qC_comentarios_nota1_2.csv")
salvar(pd.crosstab(d.regiao, d.grupo, normalize="index").mul(100).round(1).loc[ORDEM_REGIOES], "qC_comentarios_nota1_3.csv")

# 4. por mês da compra, com a taxa de atraso do mês (sugestão A)
d["mes"] = d.order_purchase_timestamp.dt.to_period("M")
mm = pd.crosstab(d.mes, d.grupo); mm["total"] = mm.sum(axis=1)
mm["log_pct"] = (100 * mm["Logística"] / mm.total).round(1)
a = etapas_entrega(); a["mes"] = a.order_purchase_timestamp.dt.to_period("M")
mm = mm[mm.total > 100].join(a.groupby("mes").agg(atraso_pct=("atrasado", "mean")).mul(100).round(1))
salvar(mm, "qC_comentarios_nota1_4.csv")
print("ok: resultados/qC_comentarios_nota1_1..4.csv")
