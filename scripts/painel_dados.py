# -*- coding: utf-8 -*-
"""Gera resultados/painel_dados.json, a base do painel index.html (cubo mês x estado x categoria + tabelas fixas)."""
import os, json, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, pedidos_padrao, RESULTADOS, EXTERNOS, INICIO_PADRAO, FIM_PADRAO

# pedidos no padrão do estudo (base.pedidos_padrao): jan/2017 a ago/2018, efetivos
d = pedidos_padrao()
top = d.groupby("cat_original").gmv.sum().sort_values(ascending=False).head(15).index
d["cat"] = np.where(d.cat_original.isin(top), d.cat_original, "outras")
agg = d.assign(
    ent_n=d.entregue.astype(int), atr_n=d.atrasado.astype(int),
    prom_s=d.prometido.where(d.entregue).fillna(0), real_s=d.real.where(d.entregue).fillna(0),
    et_n=d.et_transp.notna().astype(int), post_s=d.et_post.fillna(0), transp_s=d.et_transp.fillna(0),
    pf_n=d.post_fora.fillna(False).astype(int), av_n=d.review_score.notna().astype(int), nota_s=d.review_score.fillna(0),
    n1=(d.review_score == 1).astype(int), ped=1
).groupby(["mes", "uf", "cat"]).agg(
    ped=("ped", "sum"), gmv=("gmv", "sum"), frete=("frete", "sum"), ent=("ent_n", "sum"), atr=("atr_n", "sum"),
    prom=("prom_s", "sum"), real=("real_s", "sum"), et=("et_n", "sum"), post=("post_s", "sum"), transp=("transp_s", "sum"),
    pf=("pf_n", "sum"), av=("av_n", "sum"), nota=("nota_s", "sum"), n1=("n1", "sum")).reset_index()
# temas das notas 1: incluem pedidos cancelados (as queixas de cancelamento e estoque vêm deles), no mesmo período
r = pd.read_csv(os.path.join(RESULTADOS, "qC_rotulos_por_pedido.csv"), sep=";")[["order_id", "grupo"]]
po = ler("""SELECT o.order_id, o.order_purchase_timestamp AS ts, c.customer_state AS uf
            FROM pedidos o JOIN clientes c USING (customer_id)""")
po = po[(po.ts >= INICIO_PADRAO) & (po.ts < FIM_PADRAO)]
ci = ler("""SELECT i.order_id, i.price, pr.product_category_name AS cat FROM itens i LEFT JOIN produtos pr USING (product_id)""")
ci["cat"] = ci.cat.fillna("sem_categoria")
ci = ci.sort_values("price", ascending=False).drop_duplicates("order_id").set_index("order_id").cat
t = r.merge(po, on="order_id").join(ci, on="order_id")
t["cat"] = np.where(t.cat.isin(top), t.cat, "outras")
t["mes"] = pd.to_datetime(t.ts).dt.strftime("%Y-%m")
g = {"Logística": "log", "Lojista (separação/estoque)": "loj", "Produto": "prod", "Atendimento": "out", "Outro": "out"}
t["grupo"] = t.grupo.map(g)
T = pd.crosstab([t.mes, t.uf, t.cat], t.grupo).reindex(columns=["log", "loj", "prod", "out"], fill_value=0).reset_index()
agg = agg.merge(T, on=["mes", "uf", "cat"], how="outer").fillna(0)
for c in ["ped", "ent", "atr", "et", "pf", "av", "n1", "log", "loj", "prod", "out"]: agg[c] = agg[c].astype(int)
for c in ["gmv", "frete", "prom", "real", "post", "transp", "nota"]: agg[c] = agg[c].round(1)
# histogramas por célula para calcular MEDIANAS com qualquer filtro: prazos prometido e real em dias inteiros;
# postagem e transporte em décimos de dia. Formato de cada célula: "valor:contagem,valor:contagem".
def hist(col, fator):
    x = d.loc[d.entregue & d[col].notna(), ["mes", "uf", "cat", col]].copy()
    x["k"] = (x[col] * fator).round().clip(0, 120 * fator).astype(int)
    h = x.groupby(["mes", "uf", "cat", "k"]).size().reset_index(name="n")
    h["par"] = h.k.astype(str) + ":" + h.n.astype(str)
    return h.groupby(["mes", "uf", "cat"]).par.agg(",".join)
for col, nome, fator in [("prometido", "h_prom", 1), ("real", "h_real", 1), ("et_post", "h_post", 10), ("et_transp", "h_transp", 10)]:
    agg = agg.join(hist(col, fator).rename(nome), on=["mes", "uf", "cat"])
    agg[nome] = agg[nome].fillna("")
meses = sorted(agg.mes.unique()); ufs = sorted(agg.uf.unique()); cats = sorted(agg.cat.unique())
cols = [c for c in agg.columns if c not in ("mes", "uf", "cat")]
cubo = [[meses.index(r.mes), ufs.index(r.uf), cats.index(r.cat)] + [getattr(r, c) for c in cols] for r in agg.itertuples()]

ler_csv = lambda n: pd.read_csv(os.path.join(RESULTADOS, n), sep=";", decimal=",")
pop = pd.read_csv(os.path.join(EXTERNOS, "populacao_uf_2017.csv"))
q8b = ler_csv("q08b_renda_prazo.csv")
D = {
    "meses": meses, "ufs": ufs, "cats": cats, "cols": cols, "cubo": cubo,
    "uf_info": pop[["uf", "estado", "regiao", "populacao_2017", "renda_pc_2017"]].merge(q8b[["uf", "compradores_extra_prazo_7d"]], on="uf").to_dict("records"),
    "lojistas_mes": ler_csv("qE_retencao_lojistas_1.csv").to_dict("records"),
    "inativos": ler_csv("qE_retencao_lojistas_2.csv").to_dict("records"),
    "rfm": ler_csv("qF_rfm_lojistas_1.csv")[["segmento", "lojistas", "pct_lojistas", "pct_gmv_total", "pct_gmv_90d", "nota_media", "dos_46_da_D"]].to_dict("records"),
    "d_grupo": ler_csv("qD_lojistas_problema_1.csv").rename(columns={"Unnamed: 0": "k"}).to_dict("records"),
    "nota_atraso": ler_csv("qG_prazo_prometido_1.csv").to_dict("records"),
    "prazo_regiao": ler_csv("qG_prazo_prometido_4.csv").to_dict("records"),
    "cenarios": ler_csv("q08b_cenarios.csv").to_dict("records"),
    "rota": ler_csv("qA_onde_nasce_atraso_4.csv").to_dict("records"),
}
D["hist_fator"] = {"h_prom": 1, "h_real": 1, "h_post": 10, "h_transp": 10}
D["inativos_sens"] = ler_csv("qE_retencao_lojistas_5.csv").to_dict("records")
D["ativacao"] = ler_csv("qH_ativacao_lojistas_2.csv").to_dict("records")
D["ativacao_faixas"] = ler_csv("qH_ativacao_lojistas_1.csv").to_dict("records")
D["cat_lojistas"] = ler_csv("qI_vendas_categorias_2.csv").to_dict("records")
D["sobrevivencia"] = ler_csv("qJ_safras_lojistas_2.csv").to_dict("records")
D["amostra"] = ler_csv("qK_estabilidade_amostra_1.csv").to_dict("records")
json.dump(D, open(os.path.join(RESULTADOS, "painel_dados.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), default=float)
print(len(cubo), "linhas no cubo;", os.path.getsize(os.path.join(RESULTADOS, "painel_dados.json")) // 1024, "KB"); print(cats); print(cols)
print(agg.ped.sum(), round(agg.gmv.sum()))
