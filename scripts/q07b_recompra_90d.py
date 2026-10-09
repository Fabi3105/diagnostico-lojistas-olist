# -*- coding: utf-8 -*-
"""Q7 revisada. Recompra do comprador com janela padrão de 90 dias (decisão do Fabian).

Recompra = nova compra efetiva em outro dia, até 90 dias depois da primeira compra.
Só entram clientes cuja primeira compra foi pelo menos 90 dias antes do fim da base (janela completa).
Para comparação, também a janela de 180 dias. Lembrete: o comprador é cliente do marketplace, não da Olist."""
import pandas as pd
from base import ler, salvar

REF = pd.Timestamp("2018-09-01")
p = ler("""SELECT o.order_id, o.order_status, o.order_purchase_timestamp AS ts, c.customer_unique_id AS cli
           FROM pedidos o JOIN clientes c USING (customer_id)""")
p["ts"] = pd.to_datetime(p.ts)
p = p[~p.order_status.isin(["canceled", "unavailable"]) & (p.ts < REF)].copy()
p["dia"] = p.ts.dt.normalize()
p = p.join(p.groupby("cli").dia.min().rename("d1"), on="cli")
p["dd"] = (p.dia - p.d1).dt.days
cl = p.groupby("cli").d1.first().to_frame()
for j in (90, 180):
    cl[f"r{j}"] = cl.index.isin(p[(p.dd > 0) & (p.dd <= j)].cli.unique())
rows = []
for j in (90, 180):
    g = cl[cl.d1 <= REF - pd.Timedelta(days=j)]
    rows.append({"janela_dias": j, "clientes_com_janela_completa": len(g), "recompras": int(g[f"r{j}"].sum()), "recompra_pct": 100 * g[f"r{j}"].mean()})
salvar(pd.DataFrame(rows).round(2), "q07b_recompra_90d_1.csv", index=False)
g = cl[cl.d1 <= REF - pd.Timedelta(days=90)].copy(); g["coorte"] = g.d1.dt.to_period("Q").astype(str)
t = g.groupby("coorte").agg(clientes=("r90", "size"), recompra_90d_pct=("r90", "mean")); t["recompra_90d_pct"] *= 100
salvar(t.round(2), "q07b_recompra_90d_2.csv")
seg = p[p.dd > 0].groupby("cli").dd.min()
salvar(seg.describe(percentiles=[.25, .5, .75, .9]).round(0).rename("dias_ate_a_segunda_compra").to_frame(), "q07b_recompra_90d_3.csv")
print(pd.DataFrame(rows).round(2))
