-- Q3. Campeões de venda: os 5 produtos que mais faturam, com % do total e da categoria
-- Decisões:
--   * mesmas regras da Q1: preço dos itens sem frete; fora pedidos cancelados e indisponíveis;
--   * "mais vendem" foi lido de dois jeitos: por faturamento (consulta 1) e por unidades (consulta 2);
--   * a base não tem nome de produto, só o código; mostramos os 8 primeiros caracteres para leitura.

WITH vendas AS (
    SELECT i.product_id,
           COALESCE(pr.product_category_name, 'sem_categoria') AS categoria,
           i.order_id, i.seller_id, i.price, i.freight_value
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
por_produto AS (
    SELECT product_id, categoria,
           COUNT(*)                  AS unidades,
           COUNT(DISTINCT order_id)  AS pedidos,
           COUNT(DISTINCT seller_id) AS vendedores,
           SUM(price)                AS faturamento,
           SUM(freight_value)        AS frete
    FROM vendas
    GROUP BY product_id, categoria
),
ranqueado AS (
    SELECT *,
           100.0 * faturamento / SUM(faturamento) OVER ()                         AS pct_total,
           100.0 * faturamento / SUM(faturamento) OVER (PARTITION BY categoria)   AS pct_categoria,
           RANK() OVER (ORDER BY faturamento DESC)                                AS pos_faturamento,
           RANK() OVER (ORDER BY unidades DESC)                                   AS pos_unidades,
           RANK() OVER (PARTITION BY categoria ORDER BY faturamento DESC)         AS pos_na_categoria
    FROM por_produto
)
-- Consulta 1: top 5 por faturamento
SELECT pos_faturamento AS posicao, substr(product_id, 1, 8) AS produto, categoria,
       unidades, pedidos, vendedores,
       ROUND(faturamento, 2) AS faturamento, ROUND(frete, 2) AS frete,
       ROUND(faturamento / unidades, 2) AS preco_medio,
       ROUND(pct_total, 2) AS pct_total, ROUND(pct_categoria, 1) AS pct_categoria,
       pos_na_categoria, pos_unidades
FROM ranqueado
WHERE pos_faturamento <= 5
ORDER BY pos_faturamento;

-- Consulta 2: top 5 por unidades vendidas
WITH vendas AS (
    SELECT i.product_id, COALESCE(pr.product_category_name, 'sem_categoria') AS categoria,
           i.order_id, i.price
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
por_produto AS (
    SELECT product_id, categoria, COUNT(*) AS unidades, SUM(price) AS faturamento
    FROM vendas GROUP BY product_id, categoria
)
SELECT RANK() OVER (ORDER BY unidades DESC) AS posicao, substr(product_id, 1, 8) AS produto, categoria,
       unidades, ROUND(faturamento, 2) AS faturamento, ROUND(faturamento / unidades, 2) AS preco_medio,
       ROUND(100.0 * faturamento / SUM(faturamento) OVER (), 2) AS pct_total,
       ROUND(100.0 * faturamento / SUM(faturamento) OVER (PARTITION BY categoria), 1) AS pct_categoria
FROM por_produto
ORDER BY unidades DESC
LIMIT 5;

-- Consulta 3: concentração: quanto do faturamento fica com os 5, 50 e 500 maiores produtos
WITH por_produto AS (
    SELECT i.product_id, SUM(i.price) AS faturamento
    FROM itens i JOIN pedidos p ON p.order_id = i.order_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY i.product_id
),
r AS (SELECT faturamento, ROW_NUMBER() OVER (ORDER BY faturamento DESC) AS pos,
             SUM(faturamento) OVER () AS total, COUNT(*) OVER () AS produtos FROM por_produto)
SELECT MAX(produtos) AS produtos_vendidos,
       ROUND(100.0 * SUM(CASE WHEN pos <= 5   THEN faturamento END) / MAX(total), 2) AS pct_top5,
       ROUND(100.0 * SUM(CASE WHEN pos <= 50  THEN faturamento END) / MAX(total), 1) AS pct_top50,
       ROUND(100.0 * SUM(CASE WHEN pos <= 500 THEN faturamento END) / MAX(total), 1) AS pct_top500
FROM r;
