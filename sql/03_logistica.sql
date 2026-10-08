-- ETAPA 3: LOGÍSTICA E SATISFAÇÃO. Use só pedidos entregues com data de entrega preenchida.

-- 3.1 Prazo médio e mediano de entrega, em dias, da compra até a entrega ao cliente.
--     Dica: date_diff('day', inicio, fim); mediana com median() ou quantile_cont(x, 0.5).


-- 3.2 % de pedidos entregues depois da data estimada (order_estimated_delivery_date), no total e por mês.


-- 3.3 Prazo mediano e % de atraso por estado do cliente. Quais os 5 estados com mais atraso?


-- 3.4 A nota da avaliação (review_score) muda com o atraso? Compare a nota média e o % de notas 1 e 2
--     entre pedidos no prazo e atrasados.
--     Atenção: um pedido pode ter mais de uma avaliação. Decida como tratar e registre a decisão.


-- 3.5 Separe o atraso em faixas (no prazo, 1 a 3 dias, 4 a 7, 8 a 14, mais de 14) e mostre a nota média de cada faixa.
--     Dica: CASE WHEN.


-- CONCLUSÕES (3 a 5 linhas). Esta é a principal história do projeto: atraso derruba a satisfação?
-- - 
