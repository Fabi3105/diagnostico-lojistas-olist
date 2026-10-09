# -*- coding: utf-8 -*-
"""Sugestão E. Retenção dos lojistas (o cliente da Olist).

Como a base não tem a data de saída do lojista, usamos um indicador aproximado:
lojista "inativo" = sem nenhuma venda nos últimos 90 dias da base (referência: 01/09/2018).
Universo: lojistas com primeira venda até fev/2018 (tiveram pelo menos 6 meses para mostrar atividade).
Como a base é uma AMOSTRA, um lojista pequeno pode aparecer sem vendas só por acaso. Para separar
o acaso da saída real, calculamos a chance de 90 dias de silêncio por acaso (Poisson), a partir do
ritmo de vendas de cada lojista antes do período final."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, salvar, avaliacao_recente, etapas_entrega

REF, CORTE = pd.Timestamp("2018-09-01"), pd.Timestamp("2018-06-02")
d = ler("""SELECT i.order_id, i.seller_id, SUM(i.price) AS valor, p.order_status, p.order_purchase_timestamp AS ts,
                  p.order_delivered_customer_date AS ent, p.order_estimated_delivery_date AS est
           FROM itens i JOIN pedidos p USING (order_id) GROUP BY 1, 2""")
d["ts"] = pd.to_datetime(d.ts); d = d[d.ts < REF].copy()
d["perdido"] = d.order_status.isin(["canceled", "unavailable"])
d["mes"] = d.ts.dt.to_period("M")

# 1. lojistas ativos, novos e GMV por lojista ativo, por mês
g = d.groupby("seller_id").agg(primeira=("ts", "min"), ultima=("ts", "max"), pedidos=("order_id", "nunique"))
m = d[~d.perdido].groupby("mes").agg(gmv=("valor", "sum"), lojistas_ativos=("seller_id", "nunique"), pedidos=("order_id", "nunique"))
m["lojistas_novos"] = g.groupby(g.primeira.dt.to_period("M")).size()
m["gmv_por_lojista"] = m.gmv / m.lojistas_ativos
m["pedidos_por_lojista"] = m.pedidos / m.lojistas_ativos
salvar(m[m.index >= pd.Period("2017-01")].round(1), "qE_retencao_lojistas_1.csv")

# universo e métricas dos primeiros 90 dias de cada lojista
U = g[g.primeira < "2018-03-01"].copy()
U["inativo"] = (REF - U.ultima).dt.days > 90
av = avaliacao_recente()[["order_id", "review_score"]]
a = etapas_entrega()[["order_id", "post_fora"]]
d = d.merge(av, on="order_id", how="left").merge(a, on="order_id", how="left").merge(g[["primeira"]], left_on="seller_id", right_index=True)
d["ent"], d["est"] = pd.to_datetime(d.ent), pd.to_datetime(d.est)
d["atrasado"] = (d.ent.dt.normalize() > d.est.dt.normalize()).where(d.ent.notna())
e = d[d.seller_id.isin(U.index) & ((d.ts - d.primeira).dt.days < 90)]
U = U.join(e.groupby("seller_id").agg(ped90=("order_id", "nunique"), nota90=("review_score", "mean"),
                                      atraso90=("atrasado", "mean"), postfora90=("post_fora", "mean")))
# chance de 90 dias sem venda só por acaso (ritmo antes do período final)
pre = d[d.ts < CORTE].groupby("seller_id").order_id.nunique().reindex(U.index).fillna(0)
U["p_acaso"] = np.exp(-90 * pre / (CORTE - U.primeira).dt.days.clip(lower=1))

def tab(col):
    t = U.groupby(col).agg(lojistas=("inativo", "size"), inativos_pct=("inativo", "mean"), silencio_por_acaso_pct=("p_acaso", "mean"))
    t[["inativos_pct", "silencio_por_acaso_pct"]] *= 100
    return t.round(1)

# 2. inatividade por vendas nos primeiros 90 dias
U["vendas_primeiros_90d"] = pd.cut(U.ped90, [0, 1, 2, 4, 9, 1e9], labels=["1", "2", "3-4", "5-9", "10+"])
t2 = tab("vendas_primeiros_90d"); t2.loc["todos"] = [len(U), 100 * U.inativo.mean(), 100 * U.p_acaso.mean()]
salvar(t2.round(1), "qE_retencao_lojistas_2.csv")

# 3. por trimestre de entrada
U["coorte"] = U.primeira.dt.to_period("Q").astype(str)
salvar(tab("coorte"), "qE_retencao_lojistas_3.csv")

# 4. qualidade nos primeiros 90 dias, entre lojistas com 5+ vendas (volume parecido)
W = U[U.ped90 >= 5].copy()
W["nota_90d"] = pd.cut(W.nota90, [0, 3, 4, 4.5, 5.01], labels=["abaixo de 3", "3 a 4", "4 a 4,5", "4,5 a 5"], right=False)
W["atraso_90d"] = pd.cut(W.atraso90, [-0.01, 0, 0.1, 1], labels=["0%", "até 10%", "acima de 10%"])
W["postagem_fora_90d"] = pd.cut(W.postfora90, [-0.01, 0, 0.2, 1], labels=["0%", "até 20%", "acima de 20%"])
partes = []
for col in ["nota_90d", "atraso_90d", "postagem_fora_90d"]:
    t = W.groupby(col).agg(lojistas=("inativo", "size"), inativos_pct=("inativo", "mean"))
    t["inativos_pct"] = (100 * t.inativos_pct).round(1); t.index = [f"{col}: {i}" for i in t.index]; partes.append(t)
salvar(pd.concat(partes), "qE_retencao_lojistas_4.csv")
print(f"universo {len(U)} lojistas; inativos {100*U.inativo.mean():.1f}%; esperado por acaso {100*U.p_acaso.mean():.1f}%")

# 5. sensibilidade do critério de inatividade: 60, 90 e 180 dias sem venda
#    (a chance de silêncio por acaso usa o ritmo de vendas antes de cada janela)
linhas = []
for w in [60, 90, 180]:
    corte_w = REF - pd.Timedelta(days=w)
    inat = (REF - U.ultima).dt.days > w
    pre_w = d[d.ts < corte_w].groupby("seller_id").order_id.nunique().reindex(U.index).fillna(0)
    p_w = np.exp(-w * pre_w / (corte_w - U.primeira).dt.days.clip(lower=1))
    for fx, idx in [("todos", U.index)] + [(str(c), U.index[U.vendas_primeiros_90d == c]) for c in U.vendas_primeiros_90d.cat.categories]:
        linhas.append({"janela_dias": w, "vendas_primeiros_90d": fx, "lojistas": len(idx),
                       "inativos_pct": 100 * inat[idx].mean(), "silencio_por_acaso_pct": 100 * p_w[idx].mean()})
t5 = pd.DataFrame(linhas); t5["excesso_pp"] = t5.inativos_pct - t5.silencio_por_acaso_pct
salvar(t5.round(1), "qE_retencao_lojistas_5.csv", index=False)
print(t5.round(1).to_string())
