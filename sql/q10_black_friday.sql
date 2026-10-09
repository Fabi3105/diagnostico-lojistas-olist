-- Q10. Black Friday 2017: aumento das vendas, categorias, atraso e avaliação
-- Decisões:
--   * só a Black Friday de 2017 está na base (24/11/2017); não há pedidos em nov/2016 e a base acaba antes de nov/2018;
--   * períodos: "antes" = 01/10 a 19/11/2017 (base de comparação); "semana da BF" = 20 a 26/11; "pós-BF" = 27/11 a 31/12;
--   * a semana inteira entra porque os descontos costumam começar antes da sexta e o pico se espalha;
--   * pedidos efetivos; faturamento = preço dos itens; atraso e nota só de pedidos entregues; avaliação mais recente.

WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
ped AS (
    SELECT p.order_id, p.order_status,
           CAST(p.order_purchase_timestamp AS DATE) AS dia,
           CASE WHEN CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-10-01' AND DATE '2017-11-19' THEN '1. antes (1/10 a 19/11)'
                WHEN CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-11-20' AND DATE '2017-11-26' THEN '2. semana da BF (20 a 26/11)'
                WHEN CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-11-27' AND DATE '2017-12-31' THEN '3. pós-BF (27/11 a 31/12)'
           END AS periodo,
           date_diff('day', CAST(p.order_purchase_timestamp AS DATE), CAST(p.order_delivered_customer_date AS DATE)) AS prazo_real,
           date_diff('day', CAST(p.order_purchase_timestamp AS DATE), CAST(p.order_estimated_delivery_date AS DATE)) AS prazo_prometido,
           CASE WHEN p.order_delivered_customer_date IS NULL THEN NULL
                WHEN CAST(p.order_delivered_customer_date AS DATE) > CAST(p.order_estimated_delivery_date AS DATE) THEN 1 ELSE 0 END AS atrasou,
           a.review_score AS nota
    FROM pedidos p LEFT JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
fat AS (
    SELECT order_id, SUM(price) AS valor FROM itens GROUP BY order_id
)
-- Consulta 1: volume, atraso e nota por período
SELECT periodo,
       COUNT(DISTINCT dia) AS dias,
       COUNT(*) AS pedidos,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT dia), 1) AS pedidos_por_dia,
       ROUND(SUM(f.valor) / COUNT(DISTINCT dia), 2) AS faturamento_por_dia,
       ROUND(SUM(f.valor) / COUNT(*), 2) AS ticket_medio,
       ROUND(AVG(prazo_prometido), 1) AS prazo_prometido_medio,
       median(prazo_real) AS prazo_real_mediano,
       ROUND(100.0 * AVG(atrasou), 1) AS pct_atraso,
       ROUND(AVG(CASE WHEN order_status = 'delivered' THEN nota END), 2) AS nota_media_entregues
FROM ped JOIN fat f ON f.order_id = ped.order_id
WHERE periodo IS NOT NULL
GROUP BY periodo
ORDER BY periodo;

-- Consulta 2: pedidos e faturamento dia a dia, de 13/11 a 03/12/2017
SELECT CAST(p.order_purchase_timestamp AS DATE) AS dia,
       COUNT(DISTINCT p.order_id) AS pedidos,
       ROUND(SUM(i.price), 2) AS faturamento
FROM pedidos p JOIN itens i ON i.order_id = p.order_id
WHERE p.order_status NOT IN ('canceled', 'unavailable')
  AND CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-11-13' AND DATE '2017-12-03'
GROUP BY dia
ORDER BY dia;

-- Consulta 3: categorias na semana da BF x antes (faturamento por dia e multiplicador)
WITH v AS (
    SELECT COALESCE(pr.product_category_name, 'sem_categoria') AS categoria, i.price,
           CASE WHEN CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-10-01' AND DATE '2017-11-19' THEN 'antes'
                WHEN CAST(p.order_purchase_timestamp AS DATE) BETWEEN DATE '2017-11-20' AND DATE '2017-11-26' THEN 'bf' END AS periodo
    FROM itens i
    JOIN pedidos p ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
c AS (
    SELECT categoria,
           SUM(CASE WHEN periodo = 'antes' THEN price ELSE 0 END) AS fat_antes,
           SUM(CASE WHEN periodo = 'bf' THEN price ELSE 0 END)    AS fat_bf
    FROM v WHERE periodo IS NOT NULL GROUP BY categoria
)
SELECT categoria,
       ROUND(fat_antes / 50, 2) AS fat_dia_antes,
       ROUND(fat_bf / 7, 2)     AS fat_dia_bf,
       ROUND((fat_bf / 7) / NULLIF(fat_antes / 50, 0), 2) AS multiplicador,
       ROUND(100.0 * fat_antes / SUM(fat_antes) OVER (), 2) AS pct_antes,
       ROUND(100.0 * fat_bf / SUM(fat_bf) OVER (), 2) AS pct_bf
FROM c
ORDER BY fat_bf DESC
LIMIT 15;
