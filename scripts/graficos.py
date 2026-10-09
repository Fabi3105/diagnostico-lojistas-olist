# -*- coding: utf-8 -*-
"""Gráficos do relatório (resultados/graficos/*.png), feitos a partir dos CSVs de resultados/."""
import os
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from base import RESULTADOS

OUT = os.path.join(RESULTADOS, "graficos"); os.makedirs(OUT, exist_ok=True)
AZUL, LARANJA, AQUA, AMARELO, CINZA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#a3a29c"
TXT, TXT2, GRADE = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRADE, "axes.labelcolor": TXT2,
                     "xtick.color": TXT2, "ytick.color": TXT2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8, "axes.axisbelow": True,
                     "figure.dpi": 150, "savefig.bbox": "tight", "axes.titlesize": 11, "axes.titleweight": "bold"})
ler = lambda n: pd.read_csv(os.path.join(RESULTADOS, n), sep=";", decimal=",")
vir = lambda v, casas=1: f"{v:.{casas}f}".replace(".", ",")
brl = lambda v: f"R$ {v:,.0f}".replace(",", ".")

def salvar(fig, nome):
    fig.savefig(os.path.join(OUT, nome)); plt.close(fig)

# 1. Vendas (GMV) mensais 2017 x 2018 (Q9)
d = ler("q09_faturamento_mensal_anos_1.csv")
fig, ax = plt.subplots(figsize=(7.2, 3.2))
meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
for ano, cor in [(2017, CINZA), (2018, AZUL)]:
    x = d[(d.ano == ano) & (d.mes <= (12 if ano == 2017 else 8))]
    ax.plot(x.mes, x.faturamento / 1000, color=cor, lw=2, marker="o", ms=4)
    ax.annotate(str(ano), (x.mes.iloc[-1], x.faturamento.iloc[-1] / 1000), xytext=(6, 0), textcoords="offset points",
                color=TXT, va="center", fontweight="bold")
ax.set_xticks(range(1, 13), meses); ax.set_ylabel("R$ mil"); ax.set_yticks(range(0, 1001, 250), [f"{k:,}".replace(",", ".") for k in range(0, 1001, 250)]); ax.set_ylim(0, 1100); ax.grid(axis="x", visible=False)
ax.set_title("Vendas mensais (GMV): 2018 parou num platô")
salvar(fig, "g1_vendas_mensais.png")

# 2. Nota média por dias de atraso (Q2)
d = ler("q02_atraso_avaliacao_2.csv")
rot = ["15+ dias\nadiantado", "8 a 14\nadiantado", "1 a 7\nadiantado", "no dia\nprevisto", "1 a 3 dias\nde atraso", "4 a 7\nde atraso", "8 a 14\nde atraso", "15+ dias\nde atraso"]
cores = [AZUL] * 4 + [LARANJA] * 4
fig, ax = plt.subplots(figsize=(7.2, 3.0))
b = ax.bar(rot, d.nota_media, color=cores, width=0.65)
ax.bar_label(b, labels=[vir(v) for v in d.nota_media], padding=2, color=TXT, fontsize=9)
ax.set_ylim(0, 5); ax.set_ylabel("nota média (1 a 5)"); ax.grid(axis="x", visible=False)
ax.tick_params(axis="x", labelsize=8.5); ax.set_title("A nota despenca a partir do primeiro dia de atraso")
salvar(fig, "g2_nota_atraso.png")

# 3. Etapas da entrega por região, no padrão do estudo (indicadores_padrao.py: jan/2017 a ago/2018, medianas)
ip = ler("indicadores_padrao.csv").set_index("indicador").valor
nomes = {"SE": "Sudeste", "S": "Sul", "CO": "Centro-Oeste", "NE": "Nordeste", "N": "Norte"}
regs = ["SE", "S", "CO", "NE", "N"]
post = pd.Series([ip[f"Postagem {r}, dias (mediana)"] for r in regs], index=regs)[::-1]
tr = pd.Series([ip[f"Transporte {r}, dias (mediana)"] for r in regs], index=regs)[::-1]
fig, ax = plt.subplots(figsize=(7.2, 2.8))
y = [nomes[r] for r in post.index]
ax.barh(y, post, color=AMARELO, height=0.6, label="postagem pelo lojista")
ax.barh(y, tr, left=post, color=AZUL, height=0.6, label="transporte")
for yi, p, t in zip(y, post, tr):
    ax.text(p + t + 0.3, yi, f"{vir(p)} + {vir(t)} dias", va="center", color=TXT, fontsize=9)
ax.set_xlabel("dias (mediana de cada etapa)"); ax.set_xlim(0, 24); ax.set_xticks(range(0, 23, 5)); ax.grid(axis="y", visible=False)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=9); ax.set_title("A postagem é igual em todo o país; o transporte, não")
salvar(fig, "g3_etapas_regiao.png")

# 4. Compradores por 100 mil x prazo, por estado (Q8)
d = ler("q08_estados_populacao.csv")
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.scatter(d.prazo_real_mediano, d.compradores_por_100mil, s=36, color=AZUL, edgecolor="white", linewidth=1.2, zorder=3)
DESTAQUE = {"SP", "RJ", "DF", "MG", "PR", "SC", "RS", "GO", "BA", "PE", "PA", "MA", "AM", "RR", "AL"}
for r in d.itertuples():
    if r.uf in DESTAQUE: ax.annotate(r.uf, (r.prazo_real_mediano, r.compradores_por_100mil), xytext=(4, 3), textcoords="offset points", fontsize=7.5, color=TXT2)
ax.set_xticks(range(5, 30, 5)); ax.set_xlabel("prazo real de entrega (mediana, dias)"); ax.set_ylabel("compradores por 100 mil hab.")
ax.set_title("Quanto maior o prazo, menos gente compra (correlação −0,95)")
salvar(fig, "g4_prazo_intensidade.png")

# 5. Frete como % do preço, itens de R$ 50 a 100, por região (B)
d = ler("qB_frete_estado_2.csv").set_index("regiao")
fig, ax = plt.subplots(figsize=(7.2, 2.6))
y = [nomes[r] for r in d.index][::-1]; v = d["frete_pct_50-100"][::-1]
b = ax.barh(y, v, color=AZUL, height=0.6)
ax.bar_label(b, labels=[f"{v:.0f}%" for v in v], padding=3, color=TXT, fontsize=9)
ax.set_xlim(0, 50); ax.set_xlabel("frete como % do preço do item"); ax.grid(axis="y", visible=False)
ax.set_title("Mesmo item (R$ 50 a 100): frete quase dobra longe do Sudeste")
salvar(fig, "g5_frete_regiao.png")

# 6. Temas das notas 1 (C), no período padrão (indicadores_padrao.py)
d = ler("indicadores_padrao_temas.csv").sort_values("comentarios")
gp = d.groupby("grupo").comentarios.sum() / d.comentarios.sum() * 100
rot = {"nao_recebido": "Não recebido", "incompleto": "Pedido incompleto", "produto_errado": "Produto errado",
       "qualidade_anuncio": "Qualidade / anúncio", "defeito_avaria": "Defeito / avaria", "outro": "Outro",
       "cancelamento_estoque": "Cancelamento / estoque", "falha_entrega": "Falha na entrega", "atraso": "Atraso",
       "atendimento": "Atendimento"}
cor = {"Logística": AZUL, "Lojista (separação/estoque)": LARANJA, "Produto": AQUA, "Atendimento": CINZA, "Outro": CINZA}
fig, ax = plt.subplots(figsize=(7.2, 3.6))
b = ax.barh([rot[t] for t in d.tema], d.pct, color=[cor[g] for g in d.grupo], height=0.65)
ax.bar_label(b, labels=[vir(v) + "%" for v in d.pct], padding=3, color=TXT, fontsize=8.5)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=AZUL, label=f"Entrega {vir(gp['Logística'])}%"), Patch(color=LARANJA, label=f"Erro de envio ou estoque {vir(gp['Lojista (separação/estoque)'])}%"),
                   Patch(color=AQUA, label=f"Produto {vir(gp['Produto'])}%"), Patch(color=CINZA, label=f"Atendimento e outros {vir(gp['Atendimento'] + gp['Outro'])}%")],
          frameon=False, loc="lower right", fontsize=8.5)
ax.set_xlim(0, 40); ax.set_xlabel(f"% dos {d.comentarios.sum():,} comentários de nota 1 (jan/2017 a ago/2018)".replace(",", ".")); ax.grid(axis="y", visible=False)
ax.set_title("Do que reclama quem dá nota 1 (classificação com IA)")
salvar(fig, "g6_temas_nota1.png")

# 7. Black Friday 2017: pedidos por dia (Q10)
d = ler("q10_black_friday_2.csv"); d["dia"] = pd.to_datetime(d.dia)
fig, ax = plt.subplots(figsize=(7.2, 2.8))
cores = [LARANJA if x == pd.Timestamp("2017-11-24") else AZUL for x in d.dia]
ax.bar(d.dia.dt.strftime("%d/%m"), d.pedidos, color=cores, width=0.7)
ax.annotate("24/11: 1.166 pedidos", (d.dia.dt.strftime("%d/%m").tolist().index("24/11"), 1166), xytext=(12, -4),
            textcoords="offset points", color=TXT, fontsize=9, fontweight="bold", va="top")
ax.tick_params(axis="x", labelsize=7.5, rotation=90); ax.set_ylabel("pedidos"); ax.set_yticks(range(0, 1201, 300), [f"{k:,}".replace(",", ".") for k in range(0, 1201, 300)]); ax.grid(axis="x", visible=False)
ax.set_title("Black Friday 2017: pico de 7 vezes um dia normal")
salvar(fig, "g7_black_friday.png")
print("ok:", sorted(os.listdir(OUT)))

# ---------- gráficos da perspectiva do lojista (E, F, G) ----------
# 8. Lojistas ativos, GMV e GMV por lojista, índice out/2017 = 100 (E)
d = ler("qE_retencao_lojistas_1.csv"); d = d[d.mes >= "2017-07"].reset_index(drop=True)
b = d[d.mes == "2017-10"].iloc[0]
fig, ax = plt.subplots(figsize=(7.2, 3.2))
for col, cor, nome in [("lojistas_ativos", LARANJA, "Lojistas ativos"), ("gmv", CINZA, "GMV"), ("gmv_por_lojista", AZUL, "GMV por lojista")]:
    v = 100 * d[col] / b[col]
    ax.plot(range(len(d)), v, color=cor, lw=2.2, marker="o", ms=3.5)
    ax.annotate(f"{nome} {vir(v.iloc[-1], 0)}", (len(d) - 1, v.iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", color=TXT, fontsize=9, fontweight="bold")
rot = [f"{m[5:7]}/{m[2:4]}" for m in d.mes]
ax.set_xticks(range(0, len(d), 2), rot[::2]); ax.axhline(100, color=GRADE, lw=1)
ax.set_ylabel("índice (out/2017 = 100)"); ax.grid(axis="x", visible=False); ax.set_xlim(-0.5, len(d) + 3.5)
ax.set_title("Mais lojistas dividindo as mesmas vendas")
salvar(fig, "g8_lojistas_gmv.png")

# 9. Inativos por vendas nos primeiros 90 dias: observado x acaso da amostra (E)
d = ler("qE_retencao_lojistas_2.csv"); d = d[d.vendas_primeiros_90d != "todos"]
fig, ax = plt.subplots(figsize=(7.2, 3.0))
x = range(len(d)); w = 0.38
b1 = ax.bar([i - w / 2 for i in x], d.inativos_pct, w, color=LARANJA, label="inativos (observado)")
b2 = ax.bar([i + w / 2 for i in x], d.silencio_por_acaso_pct, w, color=CINZA, label="esperado só pelo acaso da amostra")
ax.bar_label(b1, labels=[f"{vir(v, 0)}%" for v in d.inativos_pct], padding=2, fontsize=9, color=TXT)
ax.set_xticks(list(x), [f"{v} venda{'s' if v != '1' else ''}" for v in d.vendas_primeiros_90d])
ax.set_xlabel("vendas nos primeiros 90 dias do lojista"); ax.set_ylabel("% sem vendas nos 90 dias finais")
ax.set_ylim(0, 95); ax.grid(axis="x", visible=False); ax.legend(frameon=False, fontsize=9)
ax.set_title("Quem vende pouco no começo para de vender")
salvar(fig, "g9_inativos_inicio.png")

# 10. Segmentos RFM: % dos lojistas x % do GMV dos últimos 90 dias (F)
d = ler("qF_rfm_lojistas_1.csv").iloc[::-1]
fig, ax = plt.subplots(figsize=(7.2, 3.4))
y = range(len(d)); h = 0.38
ax.barh([i + h / 2 for i in y], d.pct_lojistas, h, color=CINZA, label="% dos lojistas")
b2 = ax.barh([i - h / 2 for i in y], d.pct_gmv_90d, h, color=AZUL, label="% do GMV dos últimos 90 dias")
ax.bar_label(b2, labels=[f"{vir(v, 0)}%" for v in d.pct_gmv_90d], padding=3, fontsize=8.5, color=TXT)
ax.set_yticks(list(y), [s[2:] for s in d.segmento]); ax.set_xlim(0, 75); ax.grid(axis="y", visible=False)
ax.legend(frameon=False, fontsize=8.5, loc="lower right"); ax.set_title("Segmentos de lojistas (RFM)")
salvar(fig, "g10_rfm_lojistas.png")

# 11. Prazo prometido atual x calibrado por rota, por região (G)
d = ler("qG_prazo_prometido_4.csv").set_index("regiao")
nomes = {"SE": "Sudeste", "S": "Sul", "CO": "Centro-Oeste", "NE": "Nordeste", "N": "Norte"}
fig, ax = plt.subplots(figsize=(7.2, 2.9))
y = list(range(len(d)))[::-1]
for yi, (r, row) in zip(y, d.iterrows()):
    ax.plot([row.prometido_atual, row.prometido_rota_p93], [yi, yi], color=GRADE, lw=3, zorder=1)
    ax.scatter(row.prometido_atual, yi, s=60, color=CINZA, zorder=2)
    ax.scatter(row.prometido_rota_p93, yi, s=60, color=AZUL, zorder=3)
    ax.text(42.5, yi, f"atraso {vir(row.atraso_atual_pct, 0)}% → {vir(row.atraso_rota_p93_pct, 0)}%", va="center", fontsize=8.5, color=TXT2)
ax.set_yticks(y, [nomes[r] for r in d.index]); ax.set_xlim(12, 55); ax.set_xticks(range(15, 41, 5))
ax.set_xlabel("prazo prometido (mediana, dias)"); ax.grid(axis="y", visible=False)
ax.scatter([], [], color=CINZA, label="atual"); ax.scatter([], [], color=AZUL, label="calibrado por rota")
ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.4, -0.22), ncol=2); ax.set_title("Promessa calibrada: mais curta onde a entrega é rápida")
salvar(fig, "g11_prazo_calibrado.png")
# 12. O que diferencia o lojista novo que deslancha (H)
arred = lambda v: f"{'+' if v > 0 else ''}{int(abs(v) + 0.5) * (1 if v >= 0 else -1)}"
d = ler("qH_ativacao_lojistas_2.csv")
d = d[~d.fator.str.startswith("Preço")].iloc[::-1]
cor = d.leitura.map({"aumenta a chance": AZUL, "reduz a chance": LARANJA, "sem efeito claro": CINZA})
fig, ax = plt.subplots(figsize=(7.2, 3.8))
y = list(range(len(d)))
ax.barh(y, d.efeito_pp, color=cor, height=0.6)
ax.errorbar(d.efeito_pp, y, xerr=[d.efeito_pp - d.margem_baixa_pp, d.margem_alta_pp - d.efeito_pp], fmt="none", ecolor=TXT, elinewidth=1, capsize=2)
for yi, v, lo, hi in zip(y, d.efeito_pp, d.margem_baixa_pp, d.margem_alta_pp):
    if v >= 0: ax.text(hi + 1, yi, arred(v), va="center", ha="left", fontsize=8.5, color=TXT)
    else: ax.text(lo - 1, yi, arred(v), va="center", ha="right", fontsize=8.5, color=TXT)
ax.axvline(0, color=TXT2, lw=0.8); ax.set_yticks(y, d.fator); ax.set_xlim(-30, 30); ax.grid(axis="y", visible=False)
ax.set_xlabel("efeito na chance de chegar a 5 ou mais pedidos em 90 dias\n(pontos percentuais; traço = margem de erro de 90%)")
ax.set_title("O que diferencia o lojista novo que deslancha")
salvar(fig, "g12_ativacao_lojistas.png")

# 13. Venda por lojista por categoria, jan-ago/2017 x jan-ago/2018 (I)
d = ler("qI_vendas_categorias_2.csv")
d = d[~d.cat.astype(str).str.startswith("TOTAL")].sort_values("vendas_por_lojista_var_pct", ascending=False)
nome = lambda c: (c[0].upper() + c[1:]).replace("_", " ")
fig, ax = plt.subplots(figsize=(7.2, 3.8))
y = list(range(len(d))); cor = [LARANJA if v < 0 else AZUL for v in d.vendas_por_lojista_var_pct]
ax.barh(y, d.vendas_por_lojista_var_pct, color=cor, height=0.6)
for yi, v in zip(y, d.vendas_por_lojista_var_pct):
    ax.text(v + (1.5 if v >= 0 else -1.5), yi, arred(v) + "%", va="center", ha="left" if v >= 0 else "right", fontsize=8.5, color=TXT)
ax.axvline(0, color=TXT2, lw=0.8); ax.set_yticks(y, [nome(c) for c in d.cat]); ax.set_xlim(-60, 75); ax.grid(axis="y", visible=False)
ax.set_xlabel("variação da venda por lojista ativo, jan-ago/2017 para jan-ago/2018 (%)")
ax.set_title("Onde os lojistas cresceram mais que as vendas")
salvar(fig, "g13_categorias_lojistas.png")
# 14. Curva de sobrevivência dos lojistas (J)
d = ler("qJ_safras_lojistas_2.csv")
fig, ax = plt.subplots(figsize=(7.2, 3.2))
ax.plot(d.meses_desde_a_primeira_venda, d["5+ vendas nos primeiros 90 dias"], color=AZUL, lw=2.2, marker="o", ms=3, label="5 ou mais vendas nos primeiros 90 dias")
ax.plot(d.meses_desde_a_primeira_venda, d.ativos_pct, color=CINZA, lw=2, marker="o", ms=3, label="todos os lojistas")
ax.plot(d.meses_desde_a_primeira_venda, d["até 4 vendas nos primeiros 90 dias"], color=LARANJA, lw=2.2, marker="o", ms=3, label="até 4 vendas nos primeiros 90 dias")
for col, cor in [("5+ vendas nos primeiros 90 dias", AZUL), ("ativos_pct", CINZA), ("até 4 vendas nos primeiros 90 dias", LARANJA)]:
    ax.text(18.4, d.loc[d.meses_desde_a_primeira_venda == 18, col].iloc[0], f"{vir(d.loc[d.meses_desde_a_primeira_venda == 18, col].iloc[0], 0)}%", color=cor, va="center", fontsize=9, fontweight="bold")
ax.axvline(12, color=GRADE, lw=1); ax.text(12.2, 97, "12 meses", color=TXT2, fontsize=8.5)
ax.set_xlim(0, 20); ax.set_ylim(0, 102); ax.set_xticks(range(0, 19, 3)); ax.set_xlabel("meses desde a primeira venda"); ax.set_ylabel("% ainda vendendo")
ax.grid(axis="x", visible=False); ax.legend(frameon=False, fontsize=8.5, loc="lower left")
ax.set_title("Quem vende no começo continua: curva de sobrevivência dos lojistas")
salvar(fig, "g14_sobrevivencia_lojistas.png")
print("ok: g8 a g14")
