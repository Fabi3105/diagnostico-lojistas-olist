-- ETAPA 2: VENDAS. Considere só pedidos não cancelados e não indisponíveis, salvo quando a pergunta disser outra coisa.
-- Decida e registre em comentário: qual(is) status entra(m) na conta e por quê.

-- 2.1 Faturamento por mês. Calcule de dois jeitos e compare:
--     (a) soma de price + freight_value em itens;  (b) soma de payment_value em pagamentos.
--     Eles batem? Por que podem diferir? (Responda em comentário.)


-- 2.2 Número de pedidos e ticket médio por mês (faturamento ÷ pedidos distintos).
--     Cuidado: juntar itens e pagamentos na mesma consulta multiplica linhas. Resolva com CTEs separadas.


-- 2.3 Crescimento mês contra mês do faturamento, em %.
--     Dica: LAG() OVER (ORDER BY mes).


-- 2.4 As 10 categorias com maior faturamento, com o nome em inglês e o % do total.
--     Dica: junte itens -> produtos -> categorias.


-- 2.5 Faturamento e ticket médio por estado do cliente (customer_state). Quais os 5 maiores?


-- 2.6 Formas de pagamento: % dos pedidos e % do valor por payment_type; média de parcelas no cartão.


-- CONCLUSÕES DE VENDAS (3 a 5 linhas):
-- - 
