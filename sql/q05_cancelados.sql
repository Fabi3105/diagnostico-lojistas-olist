-- Q5. Análise dos cancelados e % em relação às vendas
-- Decisões:
--   * "perdidos" = cancelados (canceled) + indisponíveis (unavailable, produto sem estoque); mostrados separados e somados;
--   * valor = soma de payment_value (todos esses pedidos têm pagamento registrado; muitos não têm itens);
--   * base de comparação = valor pago de todos os pedidos da base;
--   * etapa do cancelamento = até onde o pedido chegou antes de ser cancelado (pelas datas preenchidas).

WITH valor AS (
    SELECT order_id, SUM(payment_value) AS pago FROM pagamentos GROUP BY order_id
),
base AS (
    SELECT p.order_id, p.order_status, v.pago
    FROM pedidos p LEFT JOIN valor v ON v.order_id = p.order_id
)
-- Consulta 1: tamanho da perda
SELECT CASE WHEN order_status = 'canceled' THEN 'cancelado'
            WHEN order_status = 'unavailable' THEN 'indisponível'
            ELSE 'vendas efetivas' END AS grupo,
       COUNT(*) AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_pedidos,
       ROUND(SUM(pago), 2) AS valor,
       ROUND(100.0 * SUM(pago) / SUM(SUM(pago)) OVER (), 2) AS pct_valor,
       ROUND(SUM(pago) / COUNT(*), 2) AS ticket_medio
FROM base
GROUP BY grupo
ORDER BY pedidos DESC;

-- Consulta 2: em que etapa o pedido foi cancelado
SELECT order_status AS status,
       CASE WHEN order_delivered_customer_date IS NOT NULL THEN '4. depois de entregue'
            WHEN order_delivered_carrier_date  IS NOT NULL THEN '3. depois de enviado'
            WHEN order_approved_at             IS NOT NULL THEN '2. aprovado, antes do envio'
            ELSE                                                '1. antes da aprovação do pagamento' END AS etapa,
       COUNT(*) AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY order_status), 1) AS pct_do_status
FROM pedidos
WHERE order_status IN ('canceled', 'unavailable')
GROUP BY status, etapa
ORDER BY status, etapa;

-- Consulta 3: taxa de perda por mês (só meses com 500+ pedidos, para evitar distorção)
SELECT strftime(order_purchase_timestamp, '%Y-%m') AS mes,
       COUNT(*) AS pedidos,
       SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS cancelados,
       SUM(CASE WHEN order_status = 'unavailable' THEN 1 ELSE 0 END) AS indisponiveis,
       ROUND(100.0 * AVG(CASE WHEN order_status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END), 2) AS pct_perdidos
FROM pedidos
GROUP BY mes
HAVING COUNT(*) >= 500
ORDER BY mes;

-- Consulta 4: perda por forma de pagamento (forma principal = maior valor do pedido)
WITH principal AS (
    SELECT order_id, payment_type,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY payment_value DESC) AS n
    FROM pagamentos
)
SELECT pr.payment_type AS forma_pagamento,
       COUNT(*) AS pedidos,
       ROUND(100.0 * AVG(CASE WHEN p.order_status = 'canceled' THEN 1 ELSE 0 END), 2) AS pct_cancelados,
       ROUND(100.0 * AVG(CASE WHEN p.order_status = 'unavailable' THEN 1 ELSE 0 END), 2) AS pct_indisponiveis
FROM pedidos p JOIN principal pr ON pr.order_id = p.order_id AND pr.n = 1
GROUP BY forma_pagamento
ORDER BY pedidos DESC;

-- Consulta 5: categorias com mais cancelamentos (pedidos com itens; mínimo de 1.000 pedidos na categoria)
WITH ped_cat AS (
    SELECT DISTINCT i.order_id, COALESCE(pr.product_category_name, 'sem_categoria') AS categoria
    FROM itens i LEFT JOIN produtos pr ON pr.product_id = i.product_id
)
SELECT pc.categoria,
       COUNT(*) AS pedidos,
       SUM(CASE WHEN p.order_status = 'canceled' THEN 1 ELSE 0 END) AS cancelados,
       ROUND(100.0 * AVG(CASE WHEN p.order_status = 'canceled' THEN 1 ELSE 0 END), 2) AS pct_cancelados
FROM ped_cat pc JOIN pedidos p ON p.order_id = pc.order_id
GROUP BY pc.categoria
HAVING COUNT(*) >= 1000
ORDER BY pct_cancelados DESC
LIMIT 10;
