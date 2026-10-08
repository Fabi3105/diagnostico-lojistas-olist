-- ETAPA 6: TABELAS PARA O POWER BI (modelo estrela). Crie cada uma como VIEW e exporte para CSV.
-- Exemplo de exportação:  COPY (SELECT * FROM fato_pedidos) TO 'dados/bi/fato_pedidos.csv' (HEADER, DELIMITER ';');
-- (crie a pasta dados\bi antes)

-- 6.1 fato_pedidos: uma linha por pedido, com cliente (unique_id), datas, status, valor pago, frete,
--     número de itens, prazo em dias, atraso (sim/não, dias) e nota da avaliação.


-- 6.2 dim_cliente: uma linha por customer_unique_id, com cidade, estado, data da 1ª compra e segmento RFM.


-- 6.3 dim_produto e dim_vendedor: uma linha por produto (com categoria em português e inglês) e por vendedor.


-- 6.4 fato_itens: uma linha por item vendido (pedido, produto, vendedor, preço, frete), para análises por categoria e vendedor.


-- 6.5 Conferência: o total de valor pago em fato_pedidos bate com a soma da tabela pagamentos? Mostre os dois.
