-- Q9. Faturamento mês a mês, comparando os anos (uma linha por ano no gráfico)
-- Decisões:
--   * faturamento = preço dos itens (sem frete) de pedidos efetivos, pela data da compra; frete ao lado;
--   * 2016 tem só set, out e dez com pedidos (out é o único mês relevante) e 2018 termina em agosto
--     (set e out/2018 têm 20 pedidos e ficam de fora); comparação justa: jan a ago de 2017 x 2018.

-- Consulta 1: tabela mês x ano (formato longo, para o gráfico)
SELECT CAST(strftime(p.order_purchase_timestamp, '%Y') AS INTEGER) AS ano,
       CAST(strftime(p.order_purchase_timestamp, '%m') AS INTEGER) AS mes,
       COUNT(DISTINCT p.order_id) AS pedidos,
       ROUND(SUM(i.price), 2)         AS faturamento,
       ROUND(SUM(i.freight_value), 2) AS frete,
       ROUND(SUM(i.price) / COUNT(DISTINCT p.order_id), 2) AS ticket_medio
FROM pedidos p JOIN itens i ON i.order_id = p.order_id
WHERE p.order_status NOT IN ('canceled', 'unavailable')
  AND p.order_purchase_timestamp < TIMESTAMP '2018-09-01'
GROUP BY ano, mes
ORDER BY ano, mes;

-- Consulta 2: 2018 x 2017, mês a mês, de janeiro a agosto
WITH m AS (
    SELECT CAST(strftime(p.order_purchase_timestamp, '%Y') AS INTEGER) AS ano,
           CAST(strftime(p.order_purchase_timestamp, '%m') AS INTEGER) AS mes,
           COUNT(DISTINCT p.order_id) AS pedidos, SUM(i.price) AS fat
    FROM pedidos p JOIN itens i ON i.order_id = p.order_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY ano, mes
)
SELECT a.mes,
       ROUND(a.fat, 2) AS fat_2017, ROUND(b.fat, 2) AS fat_2018,
       ROUND(100.0 * (b.fat / a.fat - 1), 1) AS var_faturamento_pct,
       a.pedidos AS pedidos_2017, b.pedidos AS pedidos_2018,
       ROUND(100.0 * (1.0 * b.pedidos / a.pedidos - 1), 1) AS var_pedidos_pct
FROM m a JOIN m b ON b.mes = a.mes AND b.ano = 2018
WHERE a.ano = 2017 AND a.mes <= 8
ORDER BY a.mes;

-- Consulta 3: acumulado jan a ago, 2017 x 2018
WITH m AS (
    SELECT CAST(strftime(p.order_purchase_timestamp, '%Y') AS INTEGER) AS ano,
           CAST(strftime(p.order_purchase_timestamp, '%m') AS INTEGER) AS mes,
           p.order_id, i.price
    FROM pedidos p JOIN itens i ON i.order_id = p.order_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
)
SELECT ano, COUNT(DISTINCT order_id) AS pedidos, ROUND(SUM(price), 2) AS faturamento_jan_ago
FROM m WHERE mes <= 8 AND ano IN (2017, 2018)
GROUP BY ano ORDER BY ano;
