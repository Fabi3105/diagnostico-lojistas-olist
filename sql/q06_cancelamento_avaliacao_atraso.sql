-- Q6. O cancelamento tem relação com a avaliação e com o atraso?
-- Decisões:
--   * avaliação mais recente de cada pedido;
--   * como quase todo cancelamento acontece antes da entrega, o atraso é analisado de duas formas:
--     (a) prazo prometido ao cliente na compra (dias entre a compra e a data prevista) x taxa de cancelamento;
--     (b) por lojista (30+ pedidos): quem atrasa mais as entregas também cancela mais?

-- Consulta 1: nota média por status do pedido
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
)
SELECT p.order_status AS status,
       COUNT(*) AS pedidos_avaliados,
       ROUND(AVG(a.review_score), 2) AS nota_media,
       ROUND(100.0 * AVG(CASE WHEN a.review_score = 1 THEN 1 ELSE 0 END), 1) AS pct_nota_1
FROM pedidos p JOIN aval a ON a.order_id = p.order_id AND a.n = 1
GROUP BY status
HAVING COUNT(*) >= 100
ORDER BY nota_media;

-- Consulta 2: prazo prometido na compra x cancelamento
WITH x AS (
    SELECT order_status,
           date_diff('day', CAST(order_purchase_timestamp AS DATE),
                            CAST(order_estimated_delivery_date AS DATE)) AS prazo_prometido
    FROM pedidos
)
SELECT CASE WHEN prazo_prometido <= 15 THEN '1. até 15 dias'
            WHEN prazo_prometido <= 25 THEN '2. 16 a 25 dias'
            WHEN prazo_prometido <= 35 THEN '3. 26 a 35 dias'
            ELSE                            '4. mais de 35 dias' END AS prazo_prometido,
       COUNT(*) AS pedidos,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END), 2) AS pct_cancelados,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'unavailable' THEN 1 ELSE 0 END), 2) AS pct_indisponiveis
FROM x
GROUP BY 1
ORDER BY 1;

-- Consulta 3: por lojista, taxa de atraso x taxa de cancelamento (lojistas com 30+ pedidos, em 5 grupos de atraso)
WITH ped_loj AS (
    SELECT DISTINCT i.seller_id, i.order_id FROM itens i
),
loj AS (
    SELECT pl.seller_id,
           COUNT(*) AS pedidos,
           AVG(CASE WHEN p.order_status = 'canceled' THEN 1.0 ELSE 0 END) AS taxa_cancel,
           AVG(CASE WHEN p.order_status = 'delivered' AND p.order_delivered_customer_date IS NOT NULL
                    THEN CASE WHEN CAST(p.order_delivered_customer_date AS DATE)
                                   > CAST(p.order_estimated_delivery_date AS DATE) THEN 1.0 ELSE 0 END END) AS taxa_atraso
    FROM ped_loj pl JOIN pedidos p ON p.order_id = pl.order_id
    GROUP BY pl.seller_id
    HAVING COUNT(*) >= 30
),
g AS (SELECT *, NTILE(5) OVER (ORDER BY taxa_atraso) AS grupo FROM loj)
SELECT grupo AS grupo_atraso,
       COUNT(*) AS lojistas,
       ROUND(100.0 * MIN(taxa_atraso), 1) AS atraso_min,
       ROUND(100.0 * MAX(taxa_atraso), 1) AS atraso_max,
       ROUND(100.0 * SUM(taxa_cancel * pedidos) / SUM(pedidos), 2) AS pct_cancelados
FROM g
GROUP BY grupo
ORDER BY grupo;

-- Consulta 4: correlação entre atraso e cancelamento por lojista (DuckDB: corr)
WITH ped_loj AS (SELECT DISTINCT i.seller_id, i.order_id FROM itens i),
loj AS (
    SELECT pl.seller_id,
           AVG(CASE WHEN p.order_status = 'canceled' THEN 1.0 ELSE 0 END) AS taxa_cancel,
           AVG(CASE WHEN p.order_status = 'delivered' AND p.order_delivered_customer_date IS NOT NULL
                    THEN CASE WHEN CAST(p.order_delivered_customer_date AS DATE)
                                   > CAST(p.order_estimated_delivery_date AS DATE) THEN 1.0 ELSE 0 END END) AS taxa_atraso
    FROM ped_loj pl JOIN pedidos p ON p.order_id = pl.order_id
    GROUP BY pl.seller_id HAVING COUNT(*) >= 30
)
SELECT COUNT(*) AS lojistas, ROUND(corr(taxa_atraso, taxa_cancel), 2) AS corr_atraso_cancelamento FROM loj;
