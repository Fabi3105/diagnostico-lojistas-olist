-- Q8. Vendas por estado e % da população que comprou: estados compram mais por terem mais gente
--     ou pelo tempo de entrega?
-- Fonte externa: população estimada 2017 por UF (IBGE, SIDRA tabela 6579), em dados/externos/populacao_uf_2017.csv
-- Decisões:
--   * estado = estado do cliente; cliente = customer_unique_id; pedidos efetivos (fora cancelados e indisponíveis);
--   * compradores por 100 mil habitantes = intensidade de compra, que tira o efeito do tamanho da população;
--   * prazo real = mediana de dias entre a compra e a entrega, só pedidos entregues;
--   * população de 2017, ano do meio da base (set/2016 a ago/2018).

CREATE OR REPLACE TABLE populacao AS SELECT * FROM read_csv_auto('dados/externos/populacao_uf_2017.csv');

-- Consulta 1: indicadores por estado
WITH ped AS (
    SELECT c.customer_state AS uf, c.customer_unique_id AS cliente, p.order_id, p.order_status,
           p.order_purchase_timestamp AS compra, p.order_delivered_customer_date AS entrega,
           p.order_estimated_delivery_date AS previsto
    FROM pedidos p JOIN clientes c ON c.customer_id = p.customer_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
fat AS (
    SELECT p.uf, SUM(i.price) AS faturamento, SUM(i.freight_value) AS frete
    FROM ped p JOIN itens i ON i.order_id = p.order_id GROUP BY p.uf
),
ent AS (
    SELECT uf,
           median(date_diff('day', CAST(compra AS DATE), CAST(entrega AS DATE))) AS prazo_real_mediano,
           AVG(date_diff('day', CAST(compra AS DATE), CAST(previsto AS DATE)))   AS prazo_prometido_medio,
           AVG(CASE WHEN CAST(entrega AS DATE) > CAST(previsto AS DATE) THEN 1.0 ELSE 0 END) AS taxa_atraso
    FROM ped WHERE order_status = 'delivered' AND entrega IS NOT NULL GROUP BY uf
),
uf AS (
    SELECT uf, COUNT(DISTINCT cliente) AS compradores, COUNT(*) AS pedidos FROM ped GROUP BY uf
)
SELECT u.uf, po.estado, po.regiao, po.populacao_2017,
       u.compradores, u.pedidos,
       ROUND(100000.0 * u.compradores / po.populacao_2017, 1) AS compradores_por_100mil,
       ROUND(f.faturamento, 2) AS faturamento,
       ROUND(100.0 * f.faturamento / SUM(f.faturamento) OVER (), 2) AS pct_faturamento,
       ROUND(100.0 * po.populacao_2017 / SUM(po.populacao_2017) OVER (), 2) AS pct_populacao,
       ROUND(f.faturamento / po.populacao_2017, 3) AS faturamento_por_habitante,
       ROUND(f.faturamento / u.pedidos, 2) AS ticket_medio,
       ROUND(100.0 * f.frete / f.faturamento, 1) AS frete_pct_preco,
       e.prazo_real_mediano, ROUND(e.prazo_prometido_medio, 1) AS prazo_prometido_medio,
       ROUND(100.0 * e.taxa_atraso, 1) AS pct_atraso
FROM uf u
JOIN populacao po ON po.uf = u.uf
JOIN fat f ON f.uf = u.uf
JOIN ent e ON e.uf = u.uf
ORDER BY compradores_por_100mil DESC;
