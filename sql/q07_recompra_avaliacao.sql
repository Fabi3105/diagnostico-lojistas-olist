-- Q7. Quem recompra avalia melhor?
-- Decisões:
--   * cliente = customer_unique_id (a pessoa), não customer_id (que muda a cada pedido);
--   * só pedidos efetivos (fora cancelados e indisponíveis);
--   * recompra = pedido em DIA diferente do primeiro; pedidos no mesmo dia contam como uma única compra,
--     porque muitas vezes são um carrinho dividido entre lojistas;
--   * avaliação mais recente de cada pedido; "nota da 1ª compra" = média das notas dos pedidos do primeiro dia.

WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
ped AS (
    SELECT c.customer_unique_id AS cliente, p.order_id,
           CAST(p.order_purchase_timestamp AS DATE) AS dia,
           a.review_score AS nota,
           CASE WHEN p.order_delivered_customer_date IS NOT NULL
                     AND CAST(p.order_delivered_customer_date AS DATE) > CAST(p.order_estimated_delivery_date AS DATE)
                THEN 1 ELSE 0 END AS atrasou
    FROM pedidos p
    JOIN clientes c ON c.customer_id = p.customer_id
    LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
dias AS (
    SELECT cliente, dia, AVG(nota) AS nota_dia, MAX(atrasou) AS atrasou_dia,
           DENSE_RANK() OVER (PARTITION BY cliente ORDER BY dia) AS compra_n
    FROM ped GROUP BY cliente, dia
),
cli AS (
    SELECT cliente,
           MAX(compra_n) AS compras,
           MAX(CASE WHEN compra_n = 1 THEN nota_dia END) AS nota_1a,
           MAX(CASE WHEN compra_n = 2 THEN nota_dia END) AS nota_2a,
           MAX(CASE WHEN compra_n = 1 THEN atrasou_dia END) AS atrasou_1a,
           AVG(nota_dia) AS nota_media
    FROM dias GROUP BY cliente
)
-- Consulta 1: clientes de uma compra x recompradores
SELECT CASE WHEN compras = 1 THEN '1. comprou uma vez' ELSE '2. recomprou' END AS grupo,
       COUNT(*) AS clientes,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_clientes,
       ROUND(AVG(nota_1a), 2) AS nota_1a_compra,
       ROUND(AVG(nota_media), 2) AS nota_media_todas,
       ROUND(100.0 * AVG(atrasou_1a), 1) AS pct_atraso_1a_compra
FROM cli
GROUP BY grupo
ORDER BY grupo;

-- Consulta 2: chance de recomprar conforme a nota dada na 1ª compra
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
ped AS (
    SELECT c.customer_unique_id AS cliente, p.order_id,
           CAST(p.order_purchase_timestamp AS DATE) AS dia,
           a.review_score AS nota,
           CASE WHEN p.order_delivered_customer_date IS NOT NULL
                     AND CAST(p.order_delivered_customer_date AS DATE) > CAST(p.order_estimated_delivery_date AS DATE)
                THEN 1 ELSE 0 END AS atrasou
    FROM pedidos p
    JOIN clientes c ON c.customer_id = p.customer_id
    LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
dias AS (
    SELECT cliente, dia, AVG(nota) AS nota_dia, MAX(atrasou) AS atrasou_dia,
           DENSE_RANK() OVER (PARTITION BY cliente ORDER BY dia) AS compra_n
    FROM ped GROUP BY cliente, dia
),
cli AS (
    SELECT cliente,
           MAX(compra_n) AS compras,
           MAX(CASE WHEN compra_n = 1 THEN nota_dia END) AS nota_1a,
           MAX(CASE WHEN compra_n = 2 THEN nota_dia END) AS nota_2a,
           MAX(CASE WHEN compra_n = 1 THEN atrasou_dia END) AS atrasou_1a,
           AVG(nota_dia) AS nota_media
    FROM dias GROUP BY cliente
)
SELECT CAST(ROUND(nota_1a) AS INTEGER) AS nota_1a_compra, COUNT(*) AS clientes,
       ROUND(100.0 * AVG(CASE WHEN compras > 1 THEN 1 ELSE 0 END), 2) AS pct_recompraram
FROM cli WHERE nota_1a IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- Consulta 3: chance de recomprar conforme a 1ª compra atrasou ou não
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
ped AS (
    SELECT c.customer_unique_id AS cliente, p.order_id,
           CAST(p.order_purchase_timestamp AS DATE) AS dia,
           a.review_score AS nota,
           CASE WHEN p.order_delivered_customer_date IS NOT NULL
                     AND CAST(p.order_delivered_customer_date AS DATE) > CAST(p.order_estimated_delivery_date AS DATE)
                THEN 1 ELSE 0 END AS atrasou
    FROM pedidos p
    JOIN clientes c ON c.customer_id = p.customer_id
    LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
dias AS (
    SELECT cliente, dia, AVG(nota) AS nota_dia, MAX(atrasou) AS atrasou_dia,
           DENSE_RANK() OVER (PARTITION BY cliente ORDER BY dia) AS compra_n
    FROM ped GROUP BY cliente, dia
),
cli AS (
    SELECT cliente,
           MAX(compra_n) AS compras,
           MAX(CASE WHEN compra_n = 1 THEN nota_dia END) AS nota_1a,
           MAX(CASE WHEN compra_n = 2 THEN nota_dia END) AS nota_2a,
           MAX(CASE WHEN compra_n = 1 THEN atrasou_dia END) AS atrasou_1a,
           AVG(nota_dia) AS nota_media
    FROM dias GROUP BY cliente
)
SELECT CASE WHEN atrasou_1a = 1 THEN 'atrasou' ELSE 'no prazo' END AS primeira_compra, COUNT(*) AS clientes,
       ROUND(100.0 * AVG(CASE WHEN compras > 1 THEN 1 ELSE 0 END), 2) AS pct_recompraram
FROM cli GROUP BY 1 ORDER BY 1 DESC;

-- Consulta 4: entre os que recompraram, a nota da 2ª compra x a da 1ª
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
ped AS (
    SELECT c.customer_unique_id AS cliente, p.order_id,
           CAST(p.order_purchase_timestamp AS DATE) AS dia,
           a.review_score AS nota,
           CASE WHEN p.order_delivered_customer_date IS NOT NULL
                     AND CAST(p.order_delivered_customer_date AS DATE) > CAST(p.order_estimated_delivery_date AS DATE)
                THEN 1 ELSE 0 END AS atrasou
    FROM pedidos p
    JOIN clientes c ON c.customer_id = p.customer_id
    LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
dias AS (
    SELECT cliente, dia, AVG(nota) AS nota_dia, MAX(atrasou) AS atrasou_dia,
           DENSE_RANK() OVER (PARTITION BY cliente ORDER BY dia) AS compra_n
    FROM ped GROUP BY cliente, dia
),
cli AS (
    SELECT cliente,
           MAX(compra_n) AS compras,
           MAX(CASE WHEN compra_n = 1 THEN nota_dia END) AS nota_1a,
           MAX(CASE WHEN compra_n = 2 THEN nota_dia END) AS nota_2a,
           MAX(CASE WHEN compra_n = 1 THEN atrasou_dia END) AS atrasou_1a,
           AVG(nota_dia) AS nota_media
    FROM dias GROUP BY cliente
)
SELECT COUNT(*) AS recompradores_com_2_notas,
       ROUND(AVG(nota_1a), 2) AS nota_1a, ROUND(AVG(nota_2a), 2) AS nota_2a,
       ROUND(100.0 * AVG(CASE WHEN nota_2a > nota_1a THEN 1 ELSE 0 END), 1) AS pct_melhorou,
       ROUND(100.0 * AVG(CASE WHEN nota_2a < nota_1a THEN 1 ELSE 0 END), 1) AS pct_piorou
FROM cli WHERE compras > 1 AND nota_1a IS NOT NULL AND nota_2a IS NOT NULL;
