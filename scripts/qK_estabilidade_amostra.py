# -*- coding: utf-8 -*-
"""Análise K (revisão final). A amostra é estável ao longo do tempo?

A Olist diz que a base pública é amostral, sem informar o critério. Se a composição da amostra mudasse de um mês para
outro (por exemplo, mais pedidos de SP num mês, mais de uma categoria no outro), as tendências temporais do estudo
seriam suspeitas. Aqui medimos, mês a mês no período padrão, a participação de SP entre compradores e lojistas, a
participação das 5 maiores categorias, o ticket médio, a parcela de pedidos entregues e a parcela de pedidos avaliados.
Resultado: mínimo, máximo, média e desvio relativo (desvio-padrão / média) de cada indicador."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
from base import ler, salvar, pedidos_padrao

d = pedidos_padrao()
it = ler("SELECT order_id, seller_id FROM itens")
v = ler("SELECT seller_id, seller_state FROM vendedores")
x = it.merge(d[["order_id", "mes"]], on="order_id").merge(v, on="seller_id")
top5 = d.groupby("cat_original").gmv.sum().sort_values(ascending=False).head(5).index
m = pd.DataFrame({
    "pedidos": d.groupby("mes").size(),
    "compradores_SP_pct": 100 * d.groupby("mes").uf.apply(lambda s: (s == "SP").mean()),
    "lojistas_SP_pct": 100 * x.groupby("mes").seller_state.apply(lambda s: (s == "SP").mean()),
    "top5_categorias_pct": 100 * d.groupby("mes").apply(lambda t: t.gmv[t.cat_original.isin(top5)].sum() / t.gmv.sum()),
    "ticket_medio": d.groupby("mes").gmv.mean(),
    "entregues_pct": 100 * d.groupby("mes").entregue.mean(),
    "avaliados_pct": 100 * d.groupby("mes").review_score.apply(lambda s: s.notna().mean()),
}).round(1)
salvar(m, "qK_estabilidade_amostra_1.csv")
r = pd.DataFrame({"minimo": m.min(), "maximo": m.max(), "media": m.mean(), "desvio_relativo_pct": 100 * m.std() / m.mean()}).round(1)
salvar(r, "qK_estabilidade_amostra_2.csv")
print(m.to_string()); print(r.to_string())
