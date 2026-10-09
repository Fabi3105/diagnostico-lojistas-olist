# -*- coding: utf-8 -*-
"""Sugestão I (revisão final). Vendas com olhar de varejo, ligadas aos lojistas.
1. Ticket médio e itens por pedido, mês a mês (padrão do estudo: jan/2017 a ago/2018, pedidos efetivos).
2. Categorias: jan-ago/2017 x jan-ago/2018 (mesmos meses, para não misturar sazonalidade):
   vendas, lojistas ativos, vendas por lojista e lojistas novos, para ver onde a oferta cresceu mais que a demanda.
Categoria de cada venda = categoria do item; lojista ativo na categoria = vendeu ao menos um item dela no período."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, salvar, pedidos_padrao

d = pedidos_padrao()
it = ler("SELECT order_id, seller_id, price, product_id FROM itens")
m = d.groupby("mes").agg(pedidos=("order_id", "size"), vendas=("gmv", "sum"), ticket_medio=("gmv", "mean"), ticket_mediano=("gmv", "median"))
m["itens_por_pedido"] = it[it.order_id.isin(d.order_id)].groupby("order_id").size().reindex(d.order_id).groupby(d.mes.values).mean()
salvar(m.round(2), "qI_vendas_categorias_1.csv")

pr = ler("SELECT product_id, product_category_name AS cat FROM produtos")
x = it.merge(d[["order_id", "ts"]], on="order_id").merge(pr, on="product_id", how="left")
x["cat"] = x.cat.fillna("sem_categoria")
x["janela"] = np.where((x.ts >= "2017-01-01") & (x.ts < "2017-09-01"), "2017",
                       np.where((x.ts >= "2018-01-01") & (x.ts < "2018-09-01"), "2018", None))
primeira = x.groupby("seller_id").ts.min()
x["lojista_novo_2018"] = x.seller_id.map(primeira) >= "2018-01-01"
w = x[x.janela.notna()]
top = w.groupby("cat").price.sum().sort_values(ascending=False).head(15).index
g = w[w.cat.isin(top)].groupby(["cat", "janela"]).agg(vendas=("price", "sum"), lojistas=("seller_id", "nunique")).unstack()
g.columns = [f"{a}_{b}" for a, b in g.columns]
g["vendas_var_pct"] = 100 * (g.vendas_2018 / g.vendas_2017 - 1)
g["lojistas_var_pct"] = 100 * (g.lojistas_2018 / g.lojistas_2017 - 1)
g["vendas_por_lojista_2017"] = g.vendas_2017 / g.lojistas_2017
g["vendas_por_lojista_2018"] = g.vendas_2018 / g.lojistas_2018
g["vendas_por_lojista_var_pct"] = 100 * (g.vendas_por_lojista_2018 / g.vendas_por_lojista_2017 - 1)
n18 = w[(w.janela == "2018") & w.cat.isin(top)]
g["lojistas_novos_2018"] = n18[n18.lojista_novo_2018].groupby("cat").seller_id.nunique()
g["pct_vendas_2018_de_novos"] = 100 * n18[n18.lojista_novo_2018].groupby("cat").price.sum() / n18.groupby("cat").price.sum()
tot = w.groupby("janela").agg(vendas=("price", "sum"), lojistas=("seller_id", "nunique"))
g.loc["TOTAL (todas as categorias)"] = [tot.vendas["2017"], tot.vendas["2018"], tot.lojistas["2017"], tot.lojistas["2018"],
    100 * (tot.vendas["2018"] / tot.vendas["2017"] - 1), 100 * (tot.lojistas["2018"] / tot.lojistas["2017"] - 1),
    tot.vendas["2017"] / tot.lojistas["2017"], tot.vendas["2018"] / tot.lojistas["2018"],
    100 * ((tot.vendas["2018"] / tot.lojistas["2018"]) / (tot.vendas["2017"] / tot.lojistas["2017"]) - 1),
    w[(w.janela == "2018") & w.lojista_novo_2018].seller_id.nunique(),
    100 * w[(w.janela == "2018") & w.lojista_novo_2018].price.sum() / tot.vendas["2018"]]
g = g.sort_values("vendas_2018", ascending=False)
salvar(g.round(1), "qI_vendas_categorias_2.csv")
print(m.round(1).to_string()); print(g.round(1).to_string())
