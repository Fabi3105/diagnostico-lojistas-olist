-- Q2. O atraso na entrega derruba a nota da avaliação?
-- Decisões:
--   * só pedidos entregues (delivered) com data de entrega ao cliente preenchida;
--   * compara datas (sem hora): entregue no próprio dia previsto conta como no prazo;
--   * dias_vs_previsto = data de entrega - data prevista (negativo = adiantado, positivo = atrasado);
--   * um pedido pode ter mais de uma avaliação: vale a mais recente (maior review_answer_timestamp).

WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
entregas AS (
    SELECT p.order_id,
           date_diff('day', CAST(p.order_estimated_delivery_date AS DATE),
                            CAST(p.order_delivered_customer_date AS DATE)) AS dias_vs_previsto,
           a.review_score AS nota
    FROM pedidos p
    JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status = 'delivered'
      AND p.order_delivered_customer_date IS NOT NULL
),
faixas AS (
    SELECT *,
           CASE WHEN dias_vs_previsto <= -15 THEN '1. 15+ dias adiantado'
                WHEN dias_vs_previsto <= -8  THEN '2. 8 a 14 dias adiantado'
                WHEN dias_vs_previsto <= -1  THEN '3. 1 a 7 dias adiantado'
                WHEN dias_vs_previsto = 0    THEN '4. no dia previsto'
                WHEN dias_vs_previsto <= 3   THEN '5. 1 a 3 dias de atraso'
                WHEN dias_vs_previsto <= 7   THEN '6. 4 a 7 dias de atraso'
                WHEN dias_vs_previsto <= 14  THEN '7. 8 a 14 dias de atraso'
                ELSE                              '8. 15+ dias de atraso' END AS faixa
    FROM entregas
)
-- Consulta 1: resumo no prazo x atrasado
SELECT CASE WHEN dias_vs_previsto > 0 THEN 'atrasado' ELSE 'no prazo' END AS situacao,
       COUNT(*)                                                       AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)             AS pct_pedidos,
       ROUND(AVG(nota), 2)                                            AS nota_media,
       ROUND(100.0 * AVG(CASE WHEN nota <= 2 THEN 1 ELSE 0 END), 1)   AS pct_notas_1_2,
       ROUND(100.0 * AVG(CASE WHEN nota = 5 THEN 1 ELSE 0 END), 1)    AS pct_nota_5
FROM faixas
GROUP BY situacao
ORDER BY situacao DESC;

-- Consulta 2: detalhe por faixa de atraso (repete as CTEs para rodar sozinha)
WITH aval AS (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
),
entregas AS (
    SELECT p.order_id,
           date_diff('day', CAST(p.order_estimated_delivery_date AS DATE),
                            CAST(p.order_delivered_customer_date AS DATE)) AS dias_vs_previsto,
           a.review_score AS nota
    FROM pedidos p
    JOIN aval a ON a.order_id = p.order_id AND a.n = 1
    WHERE p.order_status = 'delivered'
      AND p.order_delivered_customer_date IS NOT NULL
)
SELECT CASE WHEN dias_vs_previsto <= -15 THEN '1. 15+ dias adiantado'
            WHEN dias_vs_previsto <= -8  THEN '2. 8 a 14 dias adiantado'
            WHEN dias_vs_previsto <= -1  THEN '3. 1 a 7 dias adiantado'
            WHEN dias_vs_previsto = 0    THEN '4. no dia previsto'
            WHEN dias_vs_previsto <= 3   THEN '5. 1 a 3 dias de atraso'
            WHEN dias_vs_previsto <= 7   THEN '6. 4 a 7 dias de atraso'
            WHEN dias_vs_previsto <= 14  THEN '7. 8 a 14 dias de atraso'
            ELSE                              '8. 15+ dias de atraso' END AS faixa,
       COUNT(*)                                                       AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)             AS pct_pedidos,
       ROUND(AVG(nota), 2)                                            AS nota_media,
       ROUND(100.0 * AVG(CASE WHEN nota <= 2 THEN 1 ELSE 0 END), 1)   AS pct_notas_1_2,
       ROUND(100.0 * AVG(CASE WHEN nota = 5 THEN 1 ELSE 0 END), 1)    AS pct_nota_5
FROM entregas
GROUP BY faixa
ORDER BY faixa;
