# -*- coding: utf-8 -*-
"""Funções comuns dos scripts Python do estudo.

Os scripts leem uma cópia SQLite da base, criada a partir dos CSV de dados/brutos
(roda sozinho na primeira vez). Os nomes das tabelas são os mesmos de sql/00_carga.sql.

Variável de ambiente OLIST_SQLITE (opcional): caminho da cópia SQLite. Use quando a pasta do projeto estiver em
disco sincronizado ou em rede, onde o SQLite pode falhar com "disk I/O error"; aponte para um caminho local.
"""
import os, sqlite3
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTOS = os.path.join(RAIZ, "dados", "brutos")
EXTERNOS = os.path.join(RAIZ, "dados", "externos")
RESULTADOS = os.path.join(RAIZ, "resultados")
DB = os.environ.get("OLIST_SQLITE", os.path.join(RAIZ, "dados", "olist.sqlite"))  # caminho alternativo opcional

TABELAS = {
    "pedidos": "olist_orders_dataset", "itens": "olist_order_items_dataset",
    "pagamentos": "olist_order_payments_dataset", "avaliacoes": "olist_order_reviews_dataset",
    "clientes": "olist_customers_dataset", "vendedores": "olist_sellers_dataset",
    "produtos": "olist_products_dataset", "categorias": "product_category_name_translation",
}

REGIOES = {"N": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
           "NE": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
           "CO": ["DF", "GO", "MT", "MS"], "SE": ["ES", "MG", "RJ", "SP"], "S": ["PR", "RS", "SC"]}
UF_REGIAO = {uf: r for r, ufs in REGIOES.items() for uf in ufs}
ORDEM_REGIOES = ["SE", "S", "CO", "NE", "N"]


def conexao():
    if not os.path.exists(DB):
        con = sqlite3.connect(DB)
        for tabela, arquivo in TABELAS.items():
            pd.read_csv(os.path.join(BRUTOS, arquivo + ".csv")).to_sql(tabela, con, index=False)
        con.close()
    return sqlite3.connect(DB)


def ler(sql):
    with conexao() as con:
        return pd.read_sql(sql, con)


def salvar(df, nome, index=True):
    """CSV no padrão brasileiro (separador ; e vírgula decimal), como os demais resultados."""
    df.to_csv(os.path.join(RESULTADOS, nome), sep=";", decimal=",", encoding="utf-8-sig", index=index)


def avaliacao_recente():
    av = ler("SELECT order_id, review_id, review_score, review_answer_timestamp FROM avaliacoes")
    return av.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")


def etapas_entrega():
    """Pedidos entregues com as etapas da entrega em dias (sugestão A)."""
    p = ler("SELECT * FROM pedidos WHERE order_status = 'delivered'")
    for c in ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
              "order_delivered_customer_date", "order_estimated_delivery_date"]:
        p[c] = pd.to_datetime(p[c])
    i = ler("SELECT order_id, seller_id, shipping_limit_date FROM itens")
    i["shipping_limit_date"] = pd.to_datetime(i["shipping_limit_date"])
    lim = i.groupby("order_id").agg(limite=("shipping_limit_date", "max"),
                                    seller=("seller_id", "first"),
                                    n_lojistas=("seller_id", "nunique")).reset_index()
    cl = ler("SELECT customer_id, customer_state FROM clientes")
    v = ler("SELECT seller_id, seller_state FROM vendedores")
    d = (p.merge(lim, on="order_id").merge(cl, on="customer_id")
          .merge(v, left_on="seller", right_on="seller_id", how="left"))
    d = d.dropna(subset=["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date"])
    dias = lambda a, b: (d[b] - d[a]).dt.total_seconds() / 86400
    d["et_aprov"] = dias("order_purchase_timestamp", "order_approved_at")
    d["et_post"] = dias("order_approved_at", "order_delivered_carrier_date")
    d["et_transp"] = dias("order_delivered_carrier_date", "order_delivered_customer_date")
    d["total"] = dias("order_purchase_timestamp", "order_delivered_customer_date")
    d = d[(d[["et_aprov", "et_post", "et_transp"]] >= 0).all(axis=1)].copy()   # exclui erros de registro
    d["atrasado"] = d.order_delivered_customer_date.dt.normalize() > d.order_estimated_delivery_date.dt.normalize()
    d["post_fora"] = d.order_delivered_carrier_date > d.limite
    d["regiao"] = d.customer_state.map(UF_REGIAO)
    d["mesmo_uf"] = d.customer_state == d.seller_state
    d["prometido"] = (d.order_estimated_delivery_date.dt.normalize()
                      - d.order_purchase_timestamp.dt.normalize()).dt.days
    return d


# ---------------------------------------------------------------------------
# Padrão do estudo para os indicadores de acompanhamento (relatório, seção 5, e painel index.html):
#   período jan/2017 a ago/2018 (meses completos; 2016 e set-out/2018 têm poucos pedidos);
#   pedidos efetivos (sem cancelados e indisponíveis); prazos e atraso só nos entregues;
#   tempos em MEDIANA; notas em média; taxas em % do grupo indicado.
INICIO_PADRAO, FIM_PADRAO = "2017-01-01", "2018-09-01"


def pedidos_padrao():
    """Um pedido efetivo por linha, no período padrão, com valor, frete, categoria principal, estado do
    comprador, prazos, etapas da entrega e avaliação mais recente."""
    it = ler("""SELECT i.order_id, i.price, i.freight_value, pr.product_category_name AS cat
                FROM itens i LEFT JOIN produtos pr USING (product_id)""")
    it["cat"] = it.cat.fillna("sem_categoria")
    principal = it.sort_values("price", ascending=False).drop_duplicates("order_id").set_index("order_id").cat
    o = it.groupby("order_id").agg(gmv=("price", "sum"), frete=("freight_value", "sum"))
    o["cat_original"] = principal
    p = ler("""SELECT o.order_id, o.order_status, o.order_purchase_timestamp AS ts, o.order_delivered_customer_date AS ent,
                      o.order_estimated_delivery_date AS est, c.customer_state AS uf
               FROM pedidos o JOIN clientes c USING (customer_id)""")
    for c in ["ts", "ent", "est"]:
        p[c] = pd.to_datetime(p[c])
    p = p[(p.ts >= INICIO_PADRAO) & (p.ts < FIM_PADRAO) & ~p.order_status.isin(["canceled", "unavailable"])]
    d = p.join(o, on="order_id", how="inner")
    d["mes"] = d.ts.dt.strftime("%Y-%m")
    d["regiao"] = d.uf.map(UF_REGIAO)
    d["entregue"] = d.ent.notna()
    d["atrasado"] = d.entregue & (d.ent.dt.normalize() > d.est.dt.normalize())
    d["prometido"] = (d.est.dt.normalize() - d.ts.dt.normalize()).dt.days
    d["real"] = (d.ent.dt.normalize() - d.ts.dt.normalize()).dt.days
    e = etapas_entrega()[["order_id", "et_post", "et_transp", "post_fora"]]
    d = d.merge(e, on="order_id", how="left").merge(avaliacao_recente()[["order_id", "review_score"]], on="order_id", how="left")
    return d
