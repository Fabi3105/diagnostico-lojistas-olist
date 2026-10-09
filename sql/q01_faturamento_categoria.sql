-- Q1. Faturamento por categoria
-- Decisões (ver DIARIO_DECISOES.md):
--   * faturamento de produtos = soma do preço dos itens (price); o frete aparece em coluna separada
--     (receita relevante para o marketplace, mas de natureza diferente da venda do produto);
--   * entram todos os pedidos, exceto cancelados (canceled) e indisponíveis (unavailable), que não viraram venda;
--   * produtos sem categoria aparecem como 'sem_categoria'.

WITH vendas AS (
    SELECT COALESCE(pr.product_category_name, 'sem_categoria') AS categoria,
           i.order_id,
           i.price,
           i.freight_value
    FROM itens i
    JOIN pedidos  p  ON p.order_id = i.order_id
    LEFT JOIN produtos pr ON pr.product_id = i.product_id
    WHERE p.order_status NOT IN ('canceled', 'unavailable')
),
por_categoria AS (
    SELECT categoria,
           COUNT(*)                 AS itens,
           COUNT(DISTINCT order_id) AS pedidos,
           SUM(price)               AS faturamento,
           SUM(freight_value)       AS frete
    FROM vendas
    GROUP BY categoria
)
SELECT categoria,
       itens,
       pedidos,
       ROUND(faturamento, 2)                                              AS faturamento,
       ROUND(frete, 2)                                                    AS frete,
       ROUND(faturamento + frete, 2)                                      AS total_com_frete,
       ROUND(faturamento / itens, 2)                                      AS preco_medio_item,
       ROUND(100.0 * frete / faturamento, 1)                              AS frete_pct_do_preco,
       ROUND(100.0 * faturamento / SUM(faturamento) OVER (), 2)           AS pct_faturamento,
       ROUND(100.0 * SUM(faturamento) OVER (ORDER BY faturamento DESC
                                            ROWS UNBOUNDED PRECEDING)
                   / SUM(faturamento) OVER (), 1)                         AS pct_acumulado,
       RANK() OVER (ORDER BY faturamento DESC)                            AS posicao
FROM por_categoria
ORDER BY faturamento DESC;
