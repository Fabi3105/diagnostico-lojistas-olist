-- ETAPA 1: EXPLORAÇÃO. Escreva a consulta embaixo de cada pergunta.
-- Objetivo: entender a base antes de calcular qualquer indicador.

-- 1.1 Qual o período coberto? Mostre a primeira e a última data de compra (order_purchase_timestamp).
--     Dica: MIN e MAX.


-- 1.2 Quantos pedidos há em cada status (order_status)? Ordene do maior para o menor e mostre o % de cada um.
--     Dica: COUNT(*) com GROUP BY; para o %, divida pelo total com uma função de janela: SUM(COUNT(*)) OVER ().


-- 1.3 Quantos pedidos por mês? Algum mês parece incompleto (início ou fim da série)?
--     Dica: date_trunc('month', order_purchase_timestamp).


-- 1.4 Quantos pedidos entregues (status 'delivered') estão sem data de entrega ao cliente?
--     Dica: IS NULL. Anote o número: vai importar na etapa de logística.


-- 1.5 customer_id x customer_unique_id: quantos valores distintos há de cada um na tabela clientes?
--     O que isso quer dizer sobre quem é "o cliente"? (Escreva a conclusão num comentário.)


-- 1.6 Um pedido pode ter mais de um item e mais de um pagamento? Mostre o maior número de itens
--     e de linhas de pagamento num mesmo pedido.
--     Dica: agrupe por order_id e depois tire o MAX em uma consulta externa (ou CTE).


-- 1.7 Quantos produtos estão sem categoria? E quantas categorias não têm tradução na tabela categorias?
--     Dica: LEFT JOIN e IS NULL.


-- CONCLUSÕES DA EXPLORAÇÃO (escreva aqui, em comentários, 3 a 5 linhas):
-- - 
