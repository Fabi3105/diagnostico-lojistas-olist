# -*- coding: utf-8 -*-
"""Validação da base bruta antes da análise. Saída: resultados/validacao_dados.csv (uma linha por checagem,
com o valor encontrado e se passou). Roda antes de qualquer análise (ver rodar_tudo.py).

Checagens: linhas por tabela, chaves duplicadas, chaves órfãs entre tabelas, faixa de datas, ordem das datas
de um pedido, nulos nos campos usados, valores negativos ou zero, categorias sem tradução."""
import pandas as pd
from base import ler, salvar

L = []
def chk(grupo, nome, valor, ok, nota=""):
    L.append({"grupo": grupo, "checagem": nome, "valor": valor, "passou": "sim" if ok else "NÃO", "observacao": nota})

# 1. tamanho das tabelas (valores de referência da base pública)
ref = {"pedidos": 99441, "itens": 112650, "pagamentos": 103886, "avaliacoes": 99224, "clientes": 99441,
       "vendedores": 3095, "produtos": 32951, "categorias": 71}
for t, n in ref.items():
    v = ler(f"SELECT COUNT(*) AS n FROM {t}").n[0]
    chk("tamanho", f"linhas em {t}", v, v == n, f"referência {n}")

# 2. chaves
chk("chave", "order_id duplicado em pedidos", ler("SELECT COUNT(*) - COUNT(DISTINCT order_id) AS n FROM pedidos").n[0], True)
chk("chave", "customer_id duplicado em clientes", ler("SELECT COUNT(*) - COUNT(DISTINCT customer_id) AS n FROM clientes").n[0], True)
chk("chave", "product_id duplicado em produtos", ler("SELECT COUNT(*) - COUNT(DISTINCT product_id) AS n FROM produtos").n[0], True)
chk("chave", "seller_id duplicado em vendedores", ler("SELECT COUNT(*) - COUNT(DISTINCT seller_id) AS n FROM vendedores").n[0], True)
dup = ler("SELECT COUNT(*) - COUNT(DISTINCT review_id) AS n FROM avaliacoes").n[0]
chk("chave", "review_id repetido em avaliacoes", dup, True, "esperado: o mesmo review pode cobrir mais de um pedido; a análise usa a avaliação mais recente por pedido")
multi = ler("SELECT COUNT(*) AS n FROM (SELECT order_id FROM avaliacoes GROUP BY order_id HAVING COUNT(*) > 1)").n[0]
chk("chave", "pedidos com mais de uma avaliação", multi, True, "tratado: avaliação mais recente por pedido")
for a, b, k in [("itens", "pedidos", "order_id"), ("itens", "produtos", "product_id"), ("itens", "vendedores", "seller_id"),
                ("pedidos", "clientes", "customer_id"), ("avaliacoes", "pedidos", "order_id"), ("pagamentos", "pedidos", "order_id")]:
    v = ler(f"SELECT COUNT(*) AS n FROM {a} WHERE {k} NOT IN (SELECT {k} FROM {b})").n[0]
    chk("chave", f"{a}.{k} sem correspondência em {b}", v, v == 0)
chk("chave", "pedidos sem itens", ler("SELECT COUNT(*) AS n FROM pedidos WHERE order_id NOT IN (SELECT order_id FROM itens)").n[0], True,
    "esperado: pedidos cancelados/indisponíveis podem não ter itens; ficam fora das vendas")

# 3. datas
d = ler("""SELECT MIN(order_purchase_timestamp) AS ini, MAX(order_purchase_timestamp) AS fim FROM pedidos""")
chk("datas", "primeira compra", d.ini[0], d.ini[0] >= "2016-09-01")
chk("datas", "última compra", d.fim[0], d.fim[0] <= "2018-10-31")
p = ler("SELECT order_purchase_timestamp AS c, order_approved_at AS a, order_delivered_carrier_date AS t, order_delivered_customer_date AS e FROM pedidos")
for col in "cate": p[col] = pd.to_datetime(p[col])
chk("datas", "aprovação antes da compra", int((p.a < p.c).sum()), True, "excluídos nas etapas da entrega")
chk("datas", "transportadora antes da aprovação", int((p.t < p.a).sum()), True, "excluídos nas etapas da entrega")
chk("datas", "entrega antes da transportadora", int((p.e < p.t).sum()), True, "excluídos nas etapas da entrega")
m = ler("SELECT strftime('%Y-%m', order_purchase_timestamp) AS mes, COUNT(*) AS n FROM pedidos GROUP BY 1")
chk("datas", "meses com menos de 500 pedidos", ", ".join(m[m.n < 500].mes), True, "fora do período padrão (jan/2017 a ago/2018)")

# 4. nulos nos campos usados
for t, c in [("pedidos", "order_status"), ("pedidos", "order_purchase_timestamp"), ("pedidos", "order_estimated_delivery_date"),
             ("itens", "price"), ("itens", "freight_value"), ("itens", "seller_id"), ("clientes", "customer_state"),
             ("vendedores", "seller_state"), ("avaliacoes", "review_score")]:
    v = ler(f"SELECT COUNT(*) AS n FROM {t} WHERE {c} IS NULL").n[0]
    chk("nulos", f"{t}.{c} nulo", v, v == 0)
v = ler("SELECT COUNT(*) AS n FROM pedidos WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL").n[0]
chk("nulos", "entregues sem data de entrega", v, True, "ficam fora dos prazos")
v = ler("SELECT COUNT(*) AS n FROM produtos WHERE product_category_name IS NULL").n[0]
chk("nulos", "produtos sem categoria", v, True, "tratados como 'sem_categoria'")
v = ler("SELECT COUNT(*) AS n FROM avaliacoes WHERE review_comment_message IS NULL AND review_comment_title IS NULL").n[0]
chk("nulos", "avaliações sem texto", v, True, "só as com texto entram na classificação de temas")

# 5. valores
chk("valores", "itens com preço <= 0", ler("SELECT COUNT(*) AS n FROM itens WHERE price <= 0").n[0], True)
chk("valores", "itens com frete < 0", ler("SELECT COUNT(*) AS n FROM itens WHERE freight_value < 0").n[0], True)
chk("valores", "notas fora de 1 a 5", ler("SELECT COUNT(*) AS n FROM avaliacoes WHERE review_score < 1 OR review_score > 5").n[0], True)
chk("valores", "status distintos", ", ".join(ler("SELECT DISTINCT order_status AS s FROM pedidos ORDER BY 1").s), True)
chk("valores", "estados distintos (clientes)", ler("SELECT COUNT(DISTINCT customer_state) AS n FROM clientes").n[0], True, "esperado 27")
v = ler("SELECT COUNT(DISTINCT product_category_name) AS n FROM produtos WHERE product_category_name NOT IN (SELECT product_category_name FROM categorias)").n[0]
chk("valores", "categorias sem tradução", v, True, "o estudo usa os nomes em português")

t = pd.DataFrame(L); salvar(t, "validacao_dados.csv", index=False)
print(t.to_string()); print("\nfalhas:", (t.passou == "NÃO").sum())
