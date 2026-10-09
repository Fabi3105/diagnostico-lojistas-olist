-- Q3b. O frete pesa mais nos produtos que vendem em quantidade? Peso físico explica o frete?
-- (complemento da Q3 pedido pelo Fabian)
-- Decisões:
--   * frete relativo = soma do frete / soma do preço (frete como % do preço);
--   * peso = product_weight_g do cadastro do produto; itens sem peso ficam de fora das faixas;
--   * "produtos de volume" = os 100 com mais unidades vendidas.

-- Consulta 1: frete como % do preço por faixa de peso do produto
WITH v AS (
    SELECT i.price, i.freight_value, pr.product_weight_g AS peso
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable') AND pr.product_weight_g IS NOT NULL
)
SELECT CASE WHEN peso < 300   THEN '1. até 300 g'
            WHEN peso < 1000  THEN '2. 300 g a 1 kg'
            WHEN peso < 3000  THEN '3. 1 a 3 kg'
            WHEN peso < 10000 THEN '4. 3 a 10 kg'
            ELSE                   '5. 10 kg ou mais' END AS faixa_peso,
       COUNT(*)                                       AS itens,
       ROUND(AVG(price), 2)                           AS preco_medio,
       ROUND(AVG(freight_value), 2)                   AS frete_medio,
       ROUND(100.0 * SUM(freight_value) / SUM(price), 1) AS frete_pct_preco
FROM v
GROUP BY faixa_peso
ORDER BY faixa_peso;

-- Consulta 2: produtos de volume (100 mais vendidos em unidades) x demais
WITH v AS (
    SELECT i.product_id, i.price, i.freight_value, pr.product_weight_g AS peso
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
por_produto AS (
    SELECT product_id, COUNT(*) AS unidades, SUM(price) AS fat, SUM(freight_value) AS frete, MAX(peso) AS peso
    FROM v GROUP BY product_id
),
r AS (SELECT *, ROW_NUMBER() OVER (ORDER BY unidades DESC) AS pos FROM por_produto)
SELECT CASE WHEN pos <= 100 THEN '100 mais vendidos (unidades)' ELSE 'demais produtos' END AS grupo,
       COUNT(*) AS produtos, SUM(unidades) AS unidades,
       ROUND(SUM(fat), 2) AS faturamento, ROUND(SUM(frete), 2) AS frete,
       ROUND(100.0 * SUM(frete) / SUM(fat), 1) AS frete_pct_preco,
       ROUND(SUM(fat) / SUM(unidades), 2) AS preco_medio_item
FROM r
GROUP BY grupo;

-- Consulta 3: correlação item a item (DuckDB: corr; 1 = andam juntos, 0 = sem relação)
SELECT ROUND(corr(pr.product_weight_g, i.freight_value), 2)                 AS corr_peso_frete,
       ROUND(corr(i.price, i.freight_value), 2)                             AS corr_preco_frete,
       ROUND(corr(pr.product_weight_g, i.freight_value / i.price), 2)       AS corr_peso_frete_pct
FROM itens i
JOIN pedidos p ON p.order_id = i.order_id
JOIN produtos pr ON pr.product_id = i.product_id
WHERE p.order_status NOT IN ('canceled', 'unavailable') AND pr.product_weight_g IS NOT NULL AND i.price > 0;

-- Consulta 4: frete como % do preço por faixa de preço do item
SELECT CASE WHEN i.price < 50  THEN '1. até R$ 50'
            WHEN i.price < 100 THEN '2. R$ 50 a 100'
            WHEN i.price < 200 THEN '3. R$ 100 a 200'
            WHEN i.price < 500 THEN '4. R$ 200 a 500'
            ELSE                    '5. R$ 500 ou mais' END AS faixa_preco,
       COUNT(*)                                             AS itens,
       ROUND(AVG(i.freight_value), 2)                       AS frete_medio,
       ROUND(100.0 * SUM(i.freight_value) / SUM(i.price), 1) AS frete_pct_preco
FROM itens i
JOIN pedidos p ON p.order_id = i.order_id
WHERE p.order_status NOT IN ('canceled', 'unavailable')
GROUP BY faixa_preco
ORDER BY faixa_preco;
