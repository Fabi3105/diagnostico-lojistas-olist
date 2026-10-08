-- ETAPA 4: CLIENTES. Use customer_unique_id como "a pessoa" (lembre da pergunta 1.5).

-- 4.1 Quantos clientes compraram mais de uma vez? Qual o % de recompra?


-- 4.2 Para quem recomprou: quantos dias, em média e mediana, entre a 1ª e a 2ª compra?
--     Dica: ROW_NUMBER() OVER (PARTITION BY cliente ORDER BY data) e LAG().


-- 4.3 Coortes: agrupe os clientes pelo mês da primeira compra e mostre quantos voltaram a comprar
--     em cada mês seguinte (mês 1, 2, 3...). Monte em formato longo: coorte, meses_depois, clientes.
--     Dica: CTE com a primeira compra de cada cliente; date_diff('month', ...).


-- 4.4 RFM: para cada cliente calcule Recência (dias desde a última compra até a última data da base),
--     Frequência (pedidos) e Valor (soma paga). Dê nota de 1 a 5 em cada um com NTILE(5).
--     Atenção: com recompra tão baixa, a Frequência quase não separa ninguém. Comente o que fazer.


-- 4.5 Crie segmentos simples a partir das notas (ex.: "melhores", "em risco", "novos") e mostre
--     quantos clientes e quanto valor há em cada segmento.


-- CONCLUSÕES (3 a 5 linhas):
-- - 
