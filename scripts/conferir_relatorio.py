# -*- coding: utf-8 -*-
"""Confere os números-chave do RELATORIO.md contra os CSVs de resultados/.
Cada checagem lê o valor no CSV, formata como o relatório escreve (vírgula decimal, ponto de milhar) e
procura o texto no relatório. Saída: resultados/conferencia_relatorio.csv e um resumo na tela.
Um número que não aparece no texto é um sinal de que o relatório ficou desatualizado (ou mudou de base)."""
import os, re
import pandas as pd
from base import RAIZ, RESULTADOS, salvar

rel = open(os.path.join(RAIZ, "RELATORIO.md"), encoding="utf-8").read()
ler = lambda n: pd.read_csv(os.path.join(RESULTADOS, n), sep=";", decimal=",")
ip = ler("indicadores_padrao.csv").set_index("indicador").valor

def br(v, casas=0):
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s

L = []
def chk(tema, descricao, valor, texto, arquivo):
    L.append({"tema": tema, "descricao": descricao, "valor_no_csv": valor, "texto_procurado": texto,
              "arquivo": arquivo, "esta_no_relatorio": "sim" if texto in rel else "NÃO"})

# indicadores do período padrão
chk("padrão", "GMV", ip["Vendas (GMV), R$"], "R$ " + br(ip["Vendas (GMV), R$"] / 1e6, 2) + " milhões", "indicadores_padrao.csv")
chk("padrão", "pedidos efetivos", ip["Pedidos efetivos"], br(ip["Pedidos efetivos"]) + " pedidos", "indicadores_padrao.csv")
chk("padrão", "entregues", ip["Pedidos entregues"], br(ip["Pedidos entregues"]) + " pedidos entregues", "indicadores_padrao.csv")
chk("padrão", "atraso", ip["Pedidos atrasados, %"], br(ip["Pedidos atrasados, %"], 1) + "%", "indicadores_padrao.csv")
chk("padrão", "nota média", ip["Nota média"], "nota média de " + br(ip["Nota média"], 2), "indicadores_padrao.csv")
chk("padrão", "notas 1", ip["Notas 1, %"], br(ip["Notas 1, %"], 1) + "%", "indicadores_padrao.csv")
chk("padrão", "postagem fora do prazo", ip["Postagem fora do prazo, %"], br(ip["Postagem fora do prazo, %"], 1) + "%", "indicadores_padrao.csv")
chk("padrão", "prazo real mediano", ip["Prazo de entrega, dias (mediana)"], f"em {br(ip['Prazo de entrega, dias (mediana)'])} dias na mediana", "indicadores_padrao.csv")
chk("padrão", "prazo prometido mediano", ip["Prazo prometido, dias (mediana)"], f"contra {br(ip['Prazo prometido, dias (mediana)'])} dias prometidos", "indicadores_padrao.csv")
chk("padrão", "transporte SE", ip["Transporte SE, dias (mediana)"], f"de {br(ip['Transporte SE, dias (mediana)'])} dias, no Sudeste", "indicadores_padrao.csv")
chk("padrão", "transporte N", ip["Transporte N, dias (mediana)"], f"a {br(ip['Transporte N, dias (mediana)'])} dias, no Norte", "indicadores_padrao.csv")
chk("padrão", "atraso NE", ip["Atraso NE, %"], "| Pedidos atrasados no Nordeste | " + br(ip["Atraso NE, %"], 1) + "% |", "indicadores_padrao.csv")
chk("padrão", "lojistas ativos ago/2018", ip["Lojistas ativos em ago/2018"], br(ip["Lojistas ativos em ago/2018"]), "indicadores_padrao.csv")
chk("padrão", "vendas por lojista ago/2018", ip["Vendas por lojista ativo em ago/2018, R$"], "R$ " + br(ip["Vendas por lojista ativo em ago/2018, R$"]), "indicadores_padrao.csv")

# lojistas
e1 = ler("qE_retencao_lojistas_1.csv").set_index("mes")
chk("lojistas", "lojistas ativos mar/2018", e1.loc["2018-03", "lojistas_ativos"], br(e1.loc["2018-03", "lojistas_ativos"]) + " para", "qE_retencao_lojistas_1.csv")
chk("lojistas", "vendas por lojista mar/2018", e1.loc["2018-03", "gmv_por_lojista"], "R$ " + br(e1.loc["2018-03", "gmv_por_lojista"]), "qE_retencao_lojistas_1.csv")
chk("lojistas", "variação lojistas mar-ago/2018", None, f"(+{round(100 * (e1.loc['2018-08', 'lojistas_ativos'] / e1.loc['2018-03', 'lojistas_ativos'] - 1))}%)", "qE_retencao_lojistas_1.csv")
chk("lojistas", "variação vendas por lojista mar-ago/2018", None, f"(−{round(100 * (1 - e1.loc['2018-08', 'gmv_por_lojista'] / e1.loc['2018-03', 'gmv_por_lojista']))}%)", "qE_retencao_lojistas_1.csv")
e2 = ler("qE_retencao_lojistas_2.csv").set_index("vendas_primeiros_90d")
chk("lojistas", "universo retenção", e2.loc["todos", "lojistas"], br(e2.loc["todos", "lojistas"]) + " lojistas", "qE_retencao_lojistas_2.csv")
chk("lojistas", "inativos", e2.loc["todos", "inativos_pct"], f"{round(e2.loc['todos', 'inativos_pct'])}% estavam inativos", "qE_retencao_lojistas_2.csv")
chk("lojistas", "acaso", e2.loc["todos", "silencio_por_acaso_pct"], f"acaso explicaria {round(e2.loc['todos', 'silencio_por_acaso_pct'])}%", "qE_retencao_lojistas_2.csv")
for k, lab in [("1", "1 venda"), ("10+", "10 ou mais")]:
    chk("lojistas", f"inativos {lab}", e2.loc[k, "inativos_pct"], f"| {lab} | {br(e2.loc[k, 'lojistas'])} | {round(e2.loc[k, 'inativos_pct'])}% |", "qE_retencao_lojistas_2.csv")
e5 = ler("qE_retencao_lojistas_5.csv"); e5 = e5[e5.vendas_primeiros_90d == "todos"].set_index("janela_dias")
chk("lojistas", "excesso 60 dias", e5.loc[60, "excesso_pp"], f"Com 60 dias sem venda, a saída real fica {round(e5.loc[60, 'excesso_pp'])} pontos", "qE_retencao_lojistas_5.csv")
chk("lojistas", "excesso 180 dias", e5.loc[180, "excesso_pp"], f"com 180 dias, {round(e5.loc[180, 'excesso_pp'])} pontos", "qE_retencao_lojistas_5.csv")
f = ler("qF_rfm_lojistas_1.csv").set_index("segmento")
chk("lojistas", "campeões", f.loc["1 Campeões", "lojistas"], f"| {br(f.loc['1 Campeões', 'lojistas'])} ({round(f.loc['1 Campeões', 'pct_lojistas'])}%) | {round(f.loc['1 Campeões', 'pct_gmv_90d'])}% |", "qF_rfm_lojistas_1.csv")
chk("lojistas", "esfriando + em risco", f.loc["3 Esfriando", "lojistas"] + f.loc["6 Em risco", "lojistas"], br(f.loc["3 Esfriando", "lojistas"] + f.loc["6 Em risco", "lojistas"]) + " (", "qF_rfm_lojistas_1.csv")
chk("lojistas", "inativos RFM", f.loc["7 Inativos", "lojistas"], br(f.loc["7 Inativos", "lojistas"]) + " (", "qF_rfm_lojistas_1.csv")
d = ler("qD_lojistas_problema_1.csv").rename(columns={"Unnamed: 0": "k"}).set_index("k")
chk("lojistas", "46 lojistas: nota 1", d.loc["taxa_nota1", "prejudicam"], f"nota 1 em {br(d.loc['taxa_nota1', 'prejudicam'], 1)}% dos pedidos, contra {br(d.loc['taxa_nota1', 'demais_30+'], 1)}%", "qD_lojistas_problema_1.csv")
chk("lojistas", "46 lojistas: % das notas 1", d.loc["pct_nota1", "prejudicam"], f"{round(d.loc['pct_fat', 'prejudicam'])}% das vendas e {round(d.loc['pct_nota1', 'prejudicam'])}% das notas 1", "qD_lojistas_problema_1.csv")
h = ler("qH_ativacao_lojistas_2.csv").set_index("fator")
for fator, lab in [("Frete acima de 40% do preço", "Frete acima de 40% do preço do produto"), ("Descrição com até 300 caracteres", "Descrição dos produtos com até 300 caracteres"),
                   ("1ª venda com nota 1 ou 2", "Primeira venda com nota 1 ou 2"), ("Categoria: cama, mesa e banho", "Categoria cama, mesa e banho"), ("Categoria: móveis e decoração", "Categoria móveis e decoração")]:
    v = h.loc[fator, "efeito_pp"]; sinal = "−" if v < 0 else "+"
    chk("ativação", fator, v, f"| {lab} | {br(h.loc[fator, 'lojistas_com_o_fator'])} | {sinal}{round(abs(v))} pontos |", "qH_ativacao_lojistas_2.csv")
h5 = ler("qH_ativacao_lojistas_5.csv").set_index("cenario").deslancharam_pct
chk("ativação", "cenário com frete e descrição", h5.iloc[2], f"passaria de {round(h5.iloc[0])}% para {round(h5.iloc[2])}%", "qH_ativacao_lojistas_5.csv")
chk("ativação", "cenário só descrição", h5.iloc[1], f"só com a descrição completa, de {round(h5.iloc[0])}% para {round(h5.iloc[1])}%", "qH_ativacao_lojistas_5.csv")
j = ler("qJ_safras_lojistas_2.csv").set_index("meses_desde_a_primeira_venda")
chk("lojistas", "sobrevivência 3/6/9/12", j.loc[12, "ativos_pct"], f"{round(j.loc[3, 'ativos_pct'])}% ainda vendem após 3 meses, {round(j.loc[6, 'ativos_pct'])}% após 6, {round(j.loc[9, 'ativos_pct'])}% após 9 e {round(j.loc[12, 'ativos_pct'])}% após 12", "qJ_safras_lojistas_2.csv")
chk("lojistas", "sobrevivência por grupo", j.loc[12, "5+ vendas nos primeiros 90 dias"], f"{round(j.loc[6, '5+ vendas nos primeiros 90 dias'])}% continuam após 6 meses e {round(j.loc[12, '5+ vendas nos primeiros 90 dias'])}% após 12; entre os demais, {round(j.loc[6, 'até 4 vendas nos primeiros 90 dias'])}% e {round(j.loc[12, 'até 4 vendas nos primeiros 90 dias'])}%", "qJ_safras_lojistas_2.csv")
k = ler("qK_estabilidade_amostra_1.csv").set_index("mes")
chk("amostra", "SP compradores início e fim", k.loc["2018-08", "compradores_SP_pct"], f"sobe de {round(k.loc['2017-01', 'compradores_SP_pct'])}%, no início de 2017, para {round(k.loc['2018-08', 'compradores_SP_pct'])}%, em agosto de 2018", "qK_estabilidade_amostra_1.csv")

# entrega
q2 = ler("q02_atraso_avaliacao_1.csv").set_index("situacao")
chk("entrega", "nota no prazo x atrasado", q2.loc["no prazo", "nota_media"], f"nota média {br(q2.loc['no prazo', 'nota_media'], 2)}; atrasados, {br(q2.loc['atrasado', 'nota_media'], 2)}", "q02_atraso_avaliacao_1.csv")
g1 = ler("qG_prazo_prometido_1.csv").set_index("dv")
chk("entrega", "nota 0/1/3 dias", g1.loc[0, "nota_media"], f"de {br(g1.loc[0, 'nota_media'], 2)}, para entregas no dia prometido, para {br(g1.loc[1, 'nota_media'], 2)} com um dia de atraso e {br(g1.loc[3, 'nota_media'], 2)} com três dias", "qG_prazo_prometido_1.csv")
a2 = ler("qA_onde_nasce_atraso_2.csv").set_index("post_fora")
chk("entrega", "postagem fora x atraso", a2.loc["postou fora do limite", "atraso_pct"], f"atrasam em {round(a2.loc['postou fora do limite', 'atraso_pct'])}% dos casos, contra {round(a2.loc['postou no limite', 'atraso_pct'])}%", "qA_onde_nasce_atraso_2.csv")
g4 = ler("qG_prazo_prometido_4.csv").set_index("regiao")
for r, nome in [("SE", "Sudeste"), ("NE", "Nordeste"), ("N", "Norte")]:
    x = g4.loc[r]
    chk("entrega", f"promessa {nome}", x.prometido_rota_p93, f"| {nome} | {br(x.prometido_atual)} dias | {br(x.prometido_rota_p93)} dias | {br(x.atraso_atual_pct, 1)}% | {br(x.atraso_rota_p93_pct, 1)}% |", "qG_prazo_prometido_4.csv")
g3 = ler("qG_prazo_prometido_3.csv").set_index("politica")
chk("entrega", "promessa mediana 23 → 21", g3.loc["por rota, percentil 93", "prometido_mediano"], f"cairia de {br(g3.loc['atual (2018)', 'prometido_mediano'])} para {br(g3.loc['por rota, percentil 93', 'prometido_mediano'])} dias", "qG_prazo_prometido_3.csv")
chk("entrega", "atraso 7,8 → 7,5", g3.loc["por rota, percentil 93", "atraso_pct"], f"({br(g3.loc['atual (2018)', 'atraso_pct'], 1)}% hoje, {br(g3.loc['por rota, percentil 93', 'atraso_pct'], 1)}% com a promessa ajustada)", "qG_prazo_prometido_3.csv")
a5 = ler("qA_onde_nasce_atraso_5.csv").set_index("periodo")
chk("entrega", "Black Friday atraso", a5.loc["semana_bf", "atraso_%"], f"atraso subiu de {br(a5.loc['antes', 'atraso_%'], 1)}% para {br(a5.loc['semana_bf', 'atraso_%'], 1)}%", "qA_onde_nasce_atraso_5.csv")
t = ler("indicadores_padrao_temas.csv"); gp = 100 * t.groupby("grupo").comentarios.sum() / t.comentarios.sum()
chk("entrega", "comentários no período", t.comentarios.sum(), f"Nos {br(t.comentarios.sum())} comentários do período", "indicadores_padrao_temas.csv")
chk("entrega", "tema entrega", gp["Logística"], f"- {br(gp['Logística'], 1)}% tratam de **entrega**", "indicadores_padrao_temas.csv")
chk("entrega", "tema envio", gp["Lojista (separação/estoque)"], f"- {br(gp['Lojista (separação/estoque)'], 1)}% tratam de **erro de envio", "indicadores_padrao_temas.csv")
chk("entrega", "tema produto", gp["Produto"], f"- {br(gp['Produto'], 1)}% tratam do **produto**", "indicadores_padrao_temas.csv")
vh = ler("qC_validacao_humana_1.csv")
chk("método", "kappa humano por tema", vh.kappa[0], f"kappa de {br(vh.kappa[0], 2)}", "qC_validacao_humana_1.csv")
chk("método", "kappa fundido", vh.kappa[1], f"concordância sobe para {round(vh.concordancia_pct[1])}% (kappa de {br(vh.kappa[1], 2)})", "qC_validacao_humana_1.csv")

# demanda
m = ler("q08b_modelo.csv")
chk("demanda", "R² renda e prazo", m.r2_renda_e_prazo[0], f"explicam {round(100 * m.r2_renda_e_prazo[0])}% da diferença", "q08b_modelo.csv")
c = ler("q08b_cenarios.csv").set_index("cenario")
for cen, lab in [("2 dias a menos em cada estado", "2 dias a menos em cada estado"), ("4 dias a menos em cada estado", "4 dias a menos em cada estado")]:
    x = c.loc[cen]
    chk("demanda", cen, x.compradores_a_mais, f"| {lab} | {round(x.compradores_a_mais / 1000)} mil | de {round(x.ic95_min / 1000)} mil a {round(x.ic95_max / 1000)} mil | +{round(x.pct_sobre_atual)}% |", "q08b_cenarios.csv")
b2 = ler("qB_frete_estado_2.csv").set_index("regiao")
chk("demanda", "frete 50-100 por região", b2.loc["SE", "frete_pct_50-100"], f"{round(b2.loc['SE', 'frete_pct_50-100'])}% do preço no Sudeste, {round(b2.loc['NE', 'frete_pct_50-100'])}% no Nordeste e {round(b2.loc['N', 'frete_pct_50-100'])}% no Norte", "qB_frete_estado_2.csv")
a4 = ler("qA_onde_nasce_atraso_4.csv").set_index("mesmo_uf")
chk("demanda", "mesmo estado: transporte", a4.loc["mesmo estado", "transp_med"], f"| {br(a4.loc['mesmo estado', 'transp_med'], 1)} dias | {br(a4.loc['outro estado', 'transp_med'], 1)} dias |", "qA_onde_nasce_atraso_4.csv")
r7 = ler("q07b_recompra_90d_1.csv").set_index("janela_dias")
chk("demanda", "recompra 90/180", r7.loc[90, "recompra_pct"], f"Só {br(r7.loc[90, 'recompra_pct'], 2)}% dos compradores fazem nova compra em até 90 dias ({br(r7.loc[180, 'recompra_pct'], 2)}% em até 180 dias)", "q07b_recompra_90d_1.csv")

# vendas
i2 = ler("qI_vendas_categorias_2.csv").set_index("cat")
for cat, lab in [("perfumaria", "Perfumaria"), ("brinquedos", "Brinquedos"), ("cool_stuff", "Cool stuff"), ("cama_mesa_banho", "Cama, mesa e banho")]:
    x = i2.loc[cat]
    chk("vendas", f"categoria {lab}", x.vendas_por_lojista_var_pct, f"| {lab} | +{round(x.lojistas_var_pct)}% | +{round(x.vendas_var_pct)}% | −{round(abs(x.vendas_por_lojista_var_pct))}% |", "qI_vendas_categorias_2.csv")
tot = i2.loc["TOTAL (todas as categorias)"]
chk("vendas", "total categorias", tot.vendas_por_lojista_var_pct, f"| Total das categorias | +{round(tot.lojistas_var_pct)}% | +{round(tot.vendas_var_pct)}% | +{round(tot.vendas_por_lojista_var_pct)}% |", "qI_vendas_categorias_2.csv")
chk("vendas", "vendas de estreantes", tot.pct_vendas_2018_de_novos, f"fizeram {round(tot.pct_vendas_2018_de_novos)}% das vendas", "qI_vendas_categorias_2.csv")
i1 = ler("qI_vendas_categorias_1.csv")
chk("vendas", "ticket mín e máx", i1.ticket_medio.min(), f"entre R$ {round(i1.ticket_medio.min())} e R$ {round(i1.ticket_medio.max())}", "qI_vendas_categorias_1.csv")

t = pd.DataFrame(L); salvar(t, "conferencia_relatorio.csv", index=False)
falhas = t[t.esta_no_relatorio == "NÃO"]
print(f"{len(t)} checagens; {len(falhas)} não encontradas no relatório")
if len(falhas): print(falhas[["tema", "descricao", "texto_procurado"]].to_string())
