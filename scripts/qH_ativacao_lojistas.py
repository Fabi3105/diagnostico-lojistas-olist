# -*- coding: utf-8 -*-
"""Sugestão H (revisão final). O que diferencia o lojista novo que deslancha do que não deslancha.

Universo: lojistas com primeira venda entre jan/2017 e mai/2018 (todos tiveram 90 dias completos
antes do fim da base, 01/09/2018). "Deslanchou" = 5 ou mais pedidos efetivos nos primeiros 90 dias.
Características medidas nos primeiros 90 dias: preço, frete em relação ao preço, fotos e descrição
dos produtos vendidos, categoria principal, estado do lojista e a experiência da primeira venda.

Cuidados:
- A base só traz produtos que venderam. Por isso NÃO usamos "número de produtos": quem vende mais
  aparece com mais produtos por definição. Fotos e descrição são médias por produto, sem esse efeito.
- A base é amostra: os volumes são menores que os reais; a comparação entre grupos continua válida.
- O modelo mostra associação, não causa. Efeitos em pontos percentuais da chance de deslanchar,
  com os demais fatores fixos; margens de 90% por bootstrap (500 reamostragens de lojistas)."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from base import ler, salvar, avaliacao_recente, etapas_entrega, UF_REGIAO

REF = pd.Timestamp("2018-09-01")
d = ler("""SELECT i.order_id, i.seller_id, i.product_id, i.price, i.freight_value, p.order_status,
                  p.order_purchase_timestamp AS ts, pr.product_category_name AS cat,
                  pr.product_photos_qty AS fotos, pr.product_description_lenght AS descr
           FROM itens i JOIN pedidos p USING (order_id) LEFT JOIN produtos pr USING (product_id)""")
d["ts"] = pd.to_datetime(d.ts)
d = d[(d.ts < REF) & ~d.order_status.isin(["canceled", "unavailable"])].copy()
prim = d.groupby("seller_id").ts.min().rename("primeira")
d = d.join(prim, on="seller_id")
U = prim[(prim >= "2017-01-01") & (prim < "2018-06-01")].to_frame()
e = d[d.seller_id.isin(U.index) & ((d.ts - d.primeira).dt.days < 90)]

# --- características nos primeiros 90 dias
U = U.join(e.groupby("seller_id").agg(ped90=("order_id", "nunique"), preco=("price", "median"),
                                      frete=("freight_value", "sum"), venda=("price", "sum")))
U["frete_pct"] = 100 * U.frete / U.venda
prod = e.drop_duplicates(["seller_id", "product_id"])
U = U.join(prod.groupby("seller_id").agg(fotos=("fotos", "mean"), descr=("descr", "mean")))
cat = e.groupby(["seller_id", "cat"]).size().reset_index(name="n").sort_values("n").drop_duplicates("seller_id", keep="last")
U = U.join(cat.set_index("seller_id").cat)
v = ler("SELECT seller_id, seller_state FROM vendedores").set_index("seller_id")
U = U.join(v)
U["origem"] = np.where(U.seller_state == "SP", "SP", U.seller_state.map(UF_REGIAO).replace({"SE": "SE (fora SP)"}))
U["coorte"] = np.where(U.primeira < "2017-07-01", "1º sem/2017", np.where(U.primeira < "2018-01-01", "2º sem/2017", "1º sem/2018"))

# experiência da primeira venda
pv = e.sort_values("ts").drop_duplicates("seller_id")[["seller_id", "order_id"]]
et = etapas_entrega()[["order_id", "atrasado", "post_fora"]]
av = avaliacao_recente()[["order_id", "review_score"]]
pv = pv.merge(et, on="order_id", how="left").merge(av, on="order_id", how="left").set_index("seller_id")
U = U.join(pv[["atrasado", "post_fora", "review_score"]])
U["deslanchou"] = U.ped90 >= 5

# --- 1. taxa de lojistas que deslancharam por faixa de cada característica
def faixa(col, bins, labels):
    return pd.cut(U[col], bins, labels=labels, right=False)

U["f_preco"] = faixa("preco", [0, 30, 60, 120, 250, 1e9], ["até R$30", "R$30-60", "R$60-120", "R$120-250", "acima de R$250"])
U["f_frete"] = faixa("frete_pct", [0, 15, 25, 40, 1e9], ["até 15%", "15-25%", "25-40%", "acima de 40%"])
U["f_fotos"] = faixa("fotos", [0, 1.5, 2.5, 4, 1e9], ["1 foto", "2 fotos", "3 fotos", "4 ou mais"])
U["f_descr"] = faixa("descr", [0, 300, 700, 1500, 1e9], ["até 300 caracteres", "300-700", "700-1.500", "acima de 1.500"])
top = U.cat.value_counts().head(10).index
U["f_cat"] = U.cat.where(U.cat.isin(top), "outras")
U["f_1a_atraso"] = U.atrasado.map({True: "atrasou", False: "no prazo"})
U["f_1a_nota"] = pd.cut(U.review_score, [0, 3, 6], labels=["nota 1-2", "nota 3-5"], right=False)

base = U.deslanchou.mean()
partes = []
for col, nome in [("f_preco", "Preço mediano"), ("f_frete", "Frete / preço"), ("f_fotos", "Fotos por produto"),
                  ("f_descr", "Descrição"), ("f_cat", "Categoria principal"), ("origem", "Estado do lojista"),
                  ("coorte", "Entrada"), ("f_1a_atraso", "1ª venda: entrega"), ("f_1a_nota", "1ª venda: nota")]:
    t = U.groupby(col).agg(lojistas=("deslanchou", "size"), deslancharam_pct=("deslanchou", "mean"),
                           pedidos_90d_mediana=("ped90", "median"))
    t["deslancharam_pct"] = (100 * t.deslancharam_pct).round(1)
    t.insert(0, "caracteristica", nome); t.index.name = "faixa"
    partes.append(t.reset_index())
t1 = pd.concat(partes)
t1 = t1[t1.lojistas >= 20]
salvar(t1, "qH_ativacao_lojistas_1.csv", index=False)

# --- 2. modelo conjunto (regressão logística, numpy): efeito de cada fator com os demais fixos,
# em pontos percentuais da chance de deslanchar, com margens por bootstrap (500 reamostragens, 90%)
M = U.dropna(subset=["preco", "frete_pct", "descr", "fotos"]).copy()
X = pd.DataFrame({
    "Preço mediano até R$30": (M.preco < 30),
    "Preço mediano acima de R$250": (M.preco >= 250),
    "Frete acima de 40% do preço": (M.frete_pct >= 40),
    "Descrição com até 300 caracteres": (M.descr < 300),
    "Apenas 1 foto por produto": (M.fotos < 1.5),
    "Lojista de SP": (M.origem == "SP"),
    "1ª venda atrasou": M.atrasado.fillna(False).astype(bool),
    "1ª venda com nota 1 ou 2": (M.review_score < 3),
    "Categoria: cama, mesa e banho": (M.cat == "cama_mesa_banho"),
    "Categoria: utilidades domésticas": (M.cat == "utilidades_domesticas"),
    "Categoria: móveis e decoração": (M.cat == "moveis_decoracao"),
    "Categoria: automotivo": (M.cat == "automotivo"),
    "Categoria: ferramentas e jardim": (M.cat == "ferramentas_jardim"),
}, index=M.index).astype(float)
y = M.deslanchou.astype(float).values

def logit(A, y, it=60):
    A = np.column_stack([np.ones(len(A)), A]); b = np.zeros(A.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-A @ b)); W = p * (1 - p)
        step = np.linalg.solve(A.T @ (A * W[:, None]) + 1e-6 * np.eye(len(b)), A.T @ (y - p))
        b = b + step
        if np.max(np.abs(step)) < 1e-8: break
    return b

def efeitos(Xv, y):
    b = logit(Xv, y); out = []
    for j in range(Xv.shape[1]):
        a1, a0 = Xv.copy(), Xv.copy(); a1[:, j] = 1; a0[:, j] = 0
        pr = lambda A: 1 / (1 + np.exp(-(b[0] + A @ b[1:])))
        out.append(100 * (pr(a1).mean() - pr(a0).mean()))
    return np.array(out)

Xv = X.values
ef = efeitos(Xv, y)
rng = np.random.default_rng(42)
boots = np.array([efeitos(Xv[ix], y[ix]) for ix in (rng.integers(0, len(y), len(y)) for _ in range(500))])
lo, hi = np.percentile(boots, [5, 95], axis=0)
t2 = pd.DataFrame({"fator": X.columns, "lojistas_com_o_fator": X.sum().astype(int).values,
                   "efeito_pp": ef, "margem_baixa_pp": lo, "margem_alta_pp": hi}).round(1)
t2["leitura"] = np.where(t2.margem_baixa_pp > 0, "aumenta a chance", np.where(t2.margem_alta_pp < 0, "reduz a chance", "sem efeito claro"))
salvar(t2, "qH_ativacao_lojistas_2.csv", index=False)

# --- 3. perfil médio de quem deslanchou x quem não deslanchou
t3 = U.groupby("deslanchou").agg(lojistas=("ped90", "size"), preco_mediano=("preco", "median"), frete_pct=("frete_pct", "median"),
                                 fotos=("fotos", "mean"), descricao=("descr", "median"),
                                 lojista_SP_pct=("origem", lambda s: 100 * (s == "SP").mean()),
                                 primeira_atrasou_pct=("atrasado", "mean"))
t3["primeira_atrasou_pct"] = 100 * t3.primeira_atrasou_pct.astype(float)
t3.index = t3.index.map({True: "deslanchou (5+ pedidos)", False: "não deslanchou"})
salvar(t3.round(1), "qH_ativacao_lojistas_3.csv")

# --- 5. cenário para meta: chance média prevista se nenhum lojista tivesse frete acima de 40% do preço
#        nem descrição com até 300 caracteres (os dois fatores que o programa de ativação pode mudar)
bfull = logit(Xv, y)
prev = lambda A: (1 / (1 + np.exp(-(bfull[0] + A @ bfull[1:])))).mean() * 100
def sem(*fatores):
    A = Xv.copy()
    for c in fatores: A[:, list(X.columns).index(c)] = 0
    return prev(A)
cen = pd.DataFrame({"cenario": ["atual (previsto pelo modelo)", "sem descrição curta (alavanca do lojista)",
                                "sem frete acima de 40% e sem descrição curta (se o lojista controlar o frete)"],
                    "deslancharam_pct": [prev(Xv), sem("Descrição com até 300 caracteres"),
                                         sem("Frete acima de 40% do preço", "Descrição com até 300 caracteres")]}).round(1)
salvar(cen, "qH_ativacao_lojistas_5.csv", index=False); print(cen.to_string())

# --- 4. sensibilidade: o mesmo modelo com outros cortes de "deslanchou" (3+ e 10+ pedidos em 90 dias)
sens = {"5+ pedidos (principal)": ef}
for k in [3, 10]:
    sens[f"{k}+ pedidos"] = efeitos(Xv, (M.ped90 >= k).astype(float).values)
# por valor vendido (evita penalizar quem vende produto caro, que naturalmente tem menos pedidos)
sens["vendas acima da mediana (R$)"] = efeitos(Xv, (M.venda >= M.venda.median()).astype(float).values)
t4 = pd.DataFrame(sens, index=X.columns).round(1); t4.index.name = "fator"
salvar(t4, "qH_ativacao_lojistas_4.csv")
print(t4.to_string())

print(f"universo {len(U)}; deslancharam {100*base:.1f}%; modelo n={len(y)}")
print(t1.to_string()); print(t2.to_string()); print(t3.round(1).to_string())
