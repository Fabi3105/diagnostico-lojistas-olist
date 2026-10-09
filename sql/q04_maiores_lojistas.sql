-- Q4. Ranking dos 5 maiores lojistas (vendedores) por faturamento
-- Decisões:
--   * faturamento = preço dos itens vendidos pelo lojista, sem frete (o frete aparece ao lado);
--   * fora pedidos cancelados e indisponíveis;
--   * nota e atraso: pedidos entregues que contêm itens do lojista; avaliação mais recente do pedido;
--   * categoria principal = a de maior faturamento do lojista.

WITH v AS (
    SELECT i.seller_id, i.order_id, i.product_id, i.price, i.freight_value,
           COALESCE(pr.product_category_name, 'sem_categoria') AS categoria
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
lojista AS (
    SELECT seller_id, COUNT(*) AS itens, COUNT(DISTINCT order_id) AS pedidos,
           COUNT(DISTINCT product_id) AS produtos, COUNT(DISTINCT categoria) AS categorias,
           SUM(price) AS faturamento, SUM(freight_value) AS frete
    FROM v GROUP BY seller_id
),
cat AS (
    SELECT seller_id, categoria,
           ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY SUM(price) DESC) AS n,
           SUM(price) AS fat_cat
    FROM v GROUP BY seller_id, categoria
),
aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
qualidade AS (
    SELECT x.seller_id,
           AVG(a.review_score) AS nota_media,
           AVG(CASE WHEN CAST(p.order_delivered_customer_date AS DATE)
                         > CAST(p.order_estimated_delivery_date AS DATE) THEN 1.0 ELSE 0 END) AS taxa_atraso
    FROM (SELECT DISTINCT seller_id, order_id FROM v) x
    JOIN pedidos p ON p.order_id = x.order_id
    LEFT JOIN aval a ON a.order_id = x.order_id AND a.n = 1
    WHERE p.order_status = 'delivered' AND p.order_delivered_customer_date IS NOT NULL
    GROUP BY x.seller_id
),
r AS (
    SELECT l.*, RANK() OVER (ORDER BY l.faturamento DESC) AS posicao,
           100.0 * l.faturamento / SUM(l.faturamento) OVER () AS pct_total
    FROM lojista l
)
-- Consulta 1: os 5 maiores
SELECT r.posicao, substr(r.seller_id, 1, 8) AS lojista, s.seller_city AS cidade, s.seller_state AS uf,
       r.pedidos, r.itens, r.produtos,
       ROUND(r.faturamento, 2) AS faturamento, ROUND(r.frete, 2) AS frete,
       ROUND(r.pct_total, 2) AS pct_total,
       c.categoria AS categoria_principal, ROUND(100.0 * c.fat_cat / r.faturamento, 0) AS pct_na_principal,
       ROUND(q.nota_media, 2) AS nota_media, ROUND(100.0 * q.taxa_atraso, 1) AS pct_atraso
FROM r
JOIN vendedores s ON s.seller_id = r.seller_id
JOIN cat c ON c.seller_id = r.seller_id AND c.n = 1
LEFT JOIN qualidade q ON q.seller_id = r.seller_id
WHERE r.posicao <= 5
ORDER BY r.posicao;

-- Consulta 2: concentração entre lojistas
WITH f AS (
    SELECT i.seller_id, SUM(i.price) AS fat
    FROM itens i JOIN pedidos p ON p.order_id = i.order_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY i.seller_id
),
r AS (SELECT fat, ROW_NUMBER() OVER (ORDER BY fat DESC) AS pos,
             SUM(fat) OVER () AS total, COUNT(*) OVER () AS n FROM f)
SELECT MAX(n) AS lojistas_com_venda,
       ROUND(100.0 * SUM(CASE WHEN pos <= 5   THEN fat END) / MAX(total), 1) AS pct_top5,
       ROUND(100.0 * SUM(CASE WHEN pos <= 50  THEN fat END) / MAX(total), 1) AS pct_top50,
       ROUND(100.0 * SUM(CASE WHEN pos <= 300 THEN fat END) / MAX(total), 1) AS pct_top300,
       ROUND(MAX(total) / MAX(n), 2) AS faturamento_medio_lojista
FROM r;

-- Consulta 3: referência geral para comparar (nota e atraso de todos os pedidos entregues)
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
)
SELECT ROUND(AVG(a.review_score), 2) AS nota_media_geral,
       ROUND(100.0 * AVG(CASE WHEN CAST(p.order_delivered_customer_date AS DATE)
                                  > CAST(p.order_estimated_delivery_date AS DATE) THEN 1.0 ELSE 0 END), 1) AS pct_atraso_geral
FROM pedidos p LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
WHERE p.order_status = 'delivered' AND p.order_delivered_customer_date IS NOT NULL;
