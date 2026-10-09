# -*- coding: utf-8 -*-
"""Q8b. Renda x prazo de entrega por estado: regressão nos 27 estados e cenário de prazo de 7 dias.
Entrada: resultados/q08_estados_populacao.csv (Q8) e dados/externos/populacao_uf_2017.csv (IBGE)."""
import os
import numpy as np, pandas as pd
from base import RESULTADOS, EXTERNOS, salvar

q8 = pd.read_csv(os.path.join(RESULTADOS, "q08_estados_populacao.csv"), sep=";", decimal=",")
ext = pd.read_csv(os.path.join(EXTERNOS, "populacao_uf_2017.csv"))
d = q8.merge(ext[["uf", "renda_pc_2017"]], on="uf")

y = np.log(d.compradores_por_100mil)
lr, pz = np.log(d.renda_pc_2017), d.prazo_real_mediano


def ols(*xs):
    X = np.column_stack([np.ones(len(y)), *xs])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ b
    return b, 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum(), pred


def parcial(a, b, c):  # correlação de a com b descontando c
    ra = a - ols_simple(a, c); rb = b - ols_simple(b, c)
    return np.corrcoef(ra, rb)[0, 1]


def ols_simple(v, x):
    X = np.column_stack([np.ones(len(v)), x]); b, *_ = np.linalg.lstsq(X, v, rcond=None); return X @ b


_, r2_renda, _ = ols(lr)
_, r2_prazo, _ = ols(pz)
b, r2_ambos, pred = ols(lr, pz)
modelo = pd.DataFrame([{
    "r2_so_renda": round(r2_renda, 2), "r2_so_prazo": round(r2_prazo, 2), "r2_renda_e_prazo": round(r2_ambos, 2),
    "coef_ln_renda": round(b[1], 3), "coef_prazo_dias": round(b[2], 4),
    "corr_renda_prazo": round(np.corrcoef(lr, pz)[0, 1], 2),
    "parcial_prazo": round(parcial(y, pz, lr), 2), "parcial_renda": round(parcial(y, lr, pz), 2)}])
salvar(modelo, "q08b_modelo.csv", index=False)

prazo_sp = float(d.loc[d.uf == "SP", "prazo_real_mediano"].iloc[0])
d["esperado_modelo"] = np.exp(pred).round(1)
d["intensidade_com_prazo_7d"] = np.exp(b[0] + b[1] * lr + b[2] * prazo_sp)
# compradores a mais = (intensidade prevista com 7 dias - intensidade observada) x população; nunca negativo
d["compradores_extra_prazo_7d"] = ((d.intensidade_com_prazo_7d - d.compradores_por_100mil).clip(lower=0)
                                   * d.populacao_2017 / 1e5)
print(modelo.T)
d["intensidade_com_prazo_7d"] = d.intensidade_com_prazo_7d.round(1)
d["compradores_extra_prazo_7d"] = d.compradores_extra_prazo_7d.round(1)
cols = ["uf", "estado", "regiao", "populacao_2017", "renda_pc_2017", "prazo_real_mediano", "compradores",
        "compradores_por_100mil", "esperado_modelo", "intensidade_com_prazo_7d", "compradores_extra_prazo_7d", "ticket_medio"]
salvar(d[cols], "q08b_renda_prazo.csv", index=False)
print("compradores extras:", round(d.compradores_extra_prazo_7d.sum()))
print(d.groupby("regiao").compradores_extra_prazo_7d.sum().round())


# --- Revisão: margem de erro (bootstrap dos 27 estados) e cenários por faixa de redução do prazo ---
# Ganho de cada estado = compradores observados x (exp(coef_prazo x redução) - 1), mantendo a renda.
# (Substitui o cálculo anterior, que somava ao efeito do prazo a diferença entre o modelo e o observado.)
rng = np.random.default_rng(1)
Xall = np.column_stack([np.ones(len(y)), lr, pz])
def coef(idx):
    b, *_ = np.linalg.lstsq(Xall[idx], y.values[idx], rcond=None); return b
B = np.array([coef(rng.integers(0, len(y), len(y))) for _ in range(2000)])
def ganho(bp, red):
    pzv = pz.values
    novo = np.full(len(pzv), prazo_sp) if red == "sp" else np.maximum(prazo_sp, pzv - red)
    return (np.clip(np.exp(bp * (novo - pzv)) - 1, 0, None) * d.compradores.values).sum()
rows = []
for red, nome in [(2, "2 dias a menos em cada estado"), (4, "4 dias a menos em cada estado"), ("sp", "prazo de SP (7 dias) em todos")]:
    g0 = ganho(b[2], red); gs = np.array([ganho(bb[2], red) for bb in B])
    rows.append({"cenario": nome, "compradores_a_mais": round(g0), "ic95_min": round(np.percentile(gs, 2.5)), "ic95_max": round(np.percentile(gs, 97.5)),
                 "pct_sobre_atual": round(100 * g0 / d.compradores.sum(), 1)})
efeito = 100 * (np.exp(-b[2]) - 1); ef_ic = np.percentile(100 * (np.exp(-B[:, 2]) - 1), [2.5, 97.5])
rows.append({"cenario": "efeito de 1 dia a menos (% de compradores por habitante)", "compradores_a_mais": round(efeito, 1),
             "ic95_min": round(ef_ic[0], 1), "ic95_max": round(ef_ic[1], 1), "pct_sobre_atual": None})
salvar(pd.DataFrame(rows), "q08b_cenarios.csv", index=False)
print(pd.DataFrame(rows))
