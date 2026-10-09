# -*- coding: utf-8 -*-
"""Sugestão F. Segmentação RFM dos lojistas (Recência, Frequência, Valor).

R = dias desde a última venda (referência 01/09/2018); F = pedidos efetivos na base; M = GMV na base.
Faixas fixas e explicáveis, em vez de quintis (com muitos empates, quintis cortariam lojistas iguais em grupos diferentes):
  1 Campeões: vendeu nos últimos 30 dias e tem 30+ pedidos
  2 Em crescimento: vendeu nos últimos 30 dias e tem 10 a 29 pedidos
  3 Esfriando: 10+ pedidos, última venda entre 31 e 90 dias atrás
  4 Novos: menos de 10 pedidos, primeira venda nos últimos 90 dias
  5 Ativos de baixo volume: menos de 10 pedidos, vendeu nos últimos 90 dias, mais de 90 dias de casa
  6 Em risco: 10+ pedidos, última venda entre 91 e 180 dias atrás
  7 Inativos: sem venda há mais de 180 dias, ou entre 91 e 180 dias com menos de 10 pedidos
Base amostral: para lojistas pequenos, parte do silêncio pode ser acaso (ver sugestão E)."""
import os, warnings; warnings.filterwarnings("ignore")
import pandas as pd
from base import ler, salvar, avaliacao_recente, etapas_entrega, RESULTADOS

REF = pd.Timestamp("2018-09-01")
d = ler("""SELECT i.order_id, i.seller_id, SUM(i.price) AS valor, p.order_status, p.order_purchase_timestamp AS ts
           FROM itens i JOIN pedidos p USING (order_id) GROUP BY 1, 2""")
d["ts"] = pd.to_datetime(d.ts)
ef = d[(d.ts < REF) & ~d.order_status.isin(["canceled", "unavailable"])]
s = ef.groupby("seller_id").agg(ultima=("ts", "max"), primeira=("ts", "min"), F=("order_id", "nunique"), M=("valor", "sum"))
s["R"] = (REF - s.ultima).dt.days
s["M90"] = ef[ef.ts >= REF - pd.Timedelta(days=90)].groupby("seller_id").valor.sum().reindex(s.index).fillna(0)

def segmento(r):
    if r.R <= 30 and r.F >= 30: return "1 Campeões"
    if r.R <= 30 and r.F >= 10: return "2 Em crescimento"
    if r.R <= 90 and r.F >= 10: return "3 Esfriando"
    if r.R <= 90 and (REF - r.primeira).days <= 90: return "4 Novos"
    if r.R <= 90: return "5 Ativos de baixo volume"
    if r.R <= 180 and r.F >= 10: return "6 Em risco"
    return "7 Inativos"
s["segmento"] = s.apply(segmento, axis=1)

x = (ef.merge(avaliacao_recente()[["order_id", "review_score"]], on="order_id", how="left")
       .merge(etapas_entrega()[["order_id", "atrasado", "post_fora"]], on="order_id", how="left"))
s = s.join(x.groupby("seller_id").agg(nota=("review_score", "mean"), nota1=("review_score", lambda v: (v == 1).mean()),
                                      atraso=("atrasado", "mean"), post_fora=("post_fora", "mean")))
d46 = pd.read_csv(os.path.join(RESULTADOS, "qD_lojistas_problema_2.csv"), sep=";", decimal=",").seller_id
s["dos_46_da_D"] = s.index.isin(d46)

t = s.groupby("segmento").agg(lojistas=("F", "size"), gmv_total=("M", "sum"), gmv_90d=("M90", "sum"), pedidos_mediana=("F", "median"),
                              dias_sem_venda_mediana=("R", "median"), nota_media=("nota", "mean"), nota1_pct=("nota1", "mean"),
                              atraso_pct=("atraso", "mean"), postagem_fora_pct=("post_fora", "mean"), dos_46_da_D=("dos_46_da_D", "sum"))
t["pct_lojistas"] = 100 * t.lojistas / t.lojistas.sum()
t["pct_gmv_total"] = 100 * t.gmv_total / t.gmv_total.sum()
t["pct_gmv_90d"] = 100 * t.gmv_90d / t.gmv_90d.sum()
t = t.astype({"atraso_pct": float, "postagem_fora_pct": float})
for k in ["nota1_pct", "atraso_pct", "postagem_fora_pct"]:
    t[k] *= 100
salvar(t.round(2), "qF_rfm_lojistas_1.csv")
salvar(s[["segmento", "R", "F", "M", "M90"]].round(2).sort_values(["segmento", "M"], ascending=[True, False]), "qF_rfm_lojistas_2.csv")
print(t[["lojistas", "pct_lojistas", "pct_gmv_total", "pct_gmv_90d", "dos_46_da_D"]].round(1))
