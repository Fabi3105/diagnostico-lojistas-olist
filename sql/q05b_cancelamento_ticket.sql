-- Q5b. Pedidos de valor mais alto são mais cancelados? (complemento da Q5 pedido pelo Fabian)
-- Decisões: valor do pedido = soma dos pagamentos; faixas fixas de valor; mediana além da média,
-- porque poucos pedidos muito caros puxam a média.

WITH v AS (
    SELECT p.order_id, p.order_status, SUM(pg.payment_value) AS valor
    FROM pedidos p JOIN pagamentos pg ON pg.order_id = p.order_id
    GROUP BY p.order_id, p.order_status
)
-- Consulta 1: taxa de perda por faixa de valor do pedido
SELECT CASE WHEN valor < 50   THEN '1. até R$ 50'
            WHEN valor < 100  THEN '2. R$ 50 a 100'
            WHEN valor < 200  THEN '3. R$ 100 a 200'
            WHEN valor < 500  THEN '4. R$ 200 a 500'
            WHEN valor < 1000 THEN '5. R$ 500 a 1.000'
            ELSE                   '6. R$ 1.000 ou mais' END AS faixa_valor,
       COUNT(*) AS pedidos,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END), 2)    AS pct_cancelados,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'unavailable' THEN 1 ELSE 0 END), 2) AS pct_indisponiveis,
       ROUND(100.0 * AVG(CASE WHEN order_status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END), 2) AS pct_perdidos
FROM v
GROUP BY faixa_valor
ORDER BY faixa_valor;

-- Consulta 2: média e mediana do valor por grupo (DuckDB: median)
WITH v AS (
    SELECT p.order_id, p.order_status, SUM(pg.payment_value) AS valor
    FROM pedidos p JOIN pagamentos pg ON pg.order_id = p.order_id
    GROUP BY p.order_id, p.order_status
)
SELECT CASE WHEN order_status = 'canceled' THEN 'cancelado'
            WHEN order_status = 'unavailable' THEN 'indisponível'
            ELSE 'vendas efetivas' END AS grupo,
       COUNT(*) AS pedidos,
       ROUND(AVG(valor), 2) AS media,
       ROUND(median(valor), 2) AS mediana
FROM v
GROUP BY grupo
ORDER BY pedidos DESC;
