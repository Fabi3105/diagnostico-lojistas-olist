# -*- coding: utf-8 -*-
"""Indicadores de acompanhamento no padrão do estudo (ver base.pedidos_padrao): período jan/2017 a ago/2018,
pedidos efetivos, tempos em mediana. São os mesmos valores que o painel index.html mostra sem filtros.
Saída: resultados/indicadores_padrao.csv (indicador, valor, definição)."""
import pandas as pd
from base import ler, salvar, pedidos_padrao

d = pedidos_padrao(); e = d[d.entregue]; av = d[d.review_score.notna()]
L = []
def add(nome, valor, definicao): L.append({"indicador": nome, "valor": valor, "definicao": definicao})

add("Pedidos efetivos", len(d), "Pedidos de jan/2017 a ago/2018, sem cancelados e indisponíveis")
add("Vendas (GMV), R$", round(d.gmv.sum(), 0), "Soma do preço dos itens, sem frete")
add("Frete, R$", round(d.frete.sum(), 0), "Soma do frete dos itens")
add("Frete / vendas, %", round(100 * d.frete.sum() / d.gmv.sum(), 1), "Soma do frete dividida pela soma das vendas")
add("Pedidos entregues", len(e), "Pedidos efetivos com data de entrega")
add("Prazo de entrega, dias (mediana)", e.real.median(), "Dias da compra à entrega, pedidos entregues")
add("Prazo prometido, dias (mediana)", e.prometido.median(), "Dias da compra à data prometida, pedidos entregues")
add("Pedidos atrasados, %", round(100 * e.atrasado.mean(), 1), "Entregues depois da data prometida / entregues")
add("Postagem pelo lojista, dias (mediana)", round(e.et_post.median(), 1), "Da aprovação do pagamento à entrega à transportadora")
add("Transporte, dias (mediana)", round(e.et_transp.median(), 1), "Da transportadora ao comprador")
add("Postagem fora do prazo, %", round(100 * e.post_fora.dropna().astype(float).mean(), 1), "Entregues à transportadora depois do prazo de envio")
add("Nota média", round(av.review_score.mean(), 2), "Avaliação mais recente de cada pedido efetivo")
add("Notas 1, %", round(100 * (av.review_score == 1).mean(), 1), "Avaliações com nota 1 / pedidos avaliados")
for r in ["SE", "S", "CO", "NE", "N"]:
    x = e[e.regiao == r]
    add(f"Transporte {r}, dias (mediana)", round(x.et_transp.median(), 1), "Por região do comprador")
    add(f"Postagem {r}, dias (mediana)", round(x.et_post.median(), 1), "Por região do comprador")
    add(f"Atraso {r}, %", round(100 * x.atrasado.mean(), 1), "Por região do comprador")
lm = pd.read_csv("../resultados/qE_retencao_lojistas_1.csv", sep=";", decimal=",").set_index("mes")
add("Lojistas ativos em ago/2018", int(lm.loc["2018-08", "lojistas_ativos"]), "Lojistas com ao menos um pedido efetivo no mês")
add("Vendas por lojista ativo em ago/2018, R$", int(lm.loc["2018-08", "gmv_por_lojista"] + 0.5), "GMV do mês / lojistas ativos no mês")
t = pd.DataFrame(L); salvar(t, "indicadores_padrao.csv", index=False); print(t.to_string())

# temas das notas 1 no período padrão (inclui pedidos cancelados, de onde vêm as queixas de estoque)
import os
from base import RESULTADOS, INICIO_PADRAO, FIM_PADRAO
r = pd.read_csv(os.path.join(RESULTADOS, "qC_rotulos_por_pedido.csv"), sep=";")
po = ler("SELECT order_id, order_purchase_timestamp AS ts FROM pedidos")
r = r.merge(po, on="order_id"); r = r[(r.ts >= INICIO_PADRAO) & (r.ts < FIM_PADRAO)]
tt = r.groupby(["tema", "grupo"]).size().reset_index(name="comentarios")
tt["pct"] = (100 * tt.comentarios / len(r)).round(1)
salvar(tt.sort_values("comentarios", ascending=False), "indicadores_padrao_temas.csv", index=False)
print(len(r), "comentários no período;", (100 * r.grupo.value_counts(normalize=True)).round(1).to_dict())
