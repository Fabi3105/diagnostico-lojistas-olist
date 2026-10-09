# Resumo da base Olist (levantamento inicial, 08/10/2026)

Marketplace brasileiro: lojistas (vendedores) vendem pela Olist em grandes sites de e-commerce. Pedidos de set/2016 a out/2018.

| Tabela | Linhas | Uma linha é | Campos principais |
|---|---|---|---|
| pedidos (orders) | 99.441 | um pedido | status, data da compra, aprovação, envio, entrega, entrega prevista |
| itens (order_items) | 112.650 | um item de um pedido | produto, vendedor, preço, frete |
| pagamentos (order_payments) | 103.886 | uma forma de pagamento de um pedido | tipo, parcelas, valor |
| avaliações (order_reviews) | 99.224 | uma avaliação | nota de 1 a 5, comentário, datas |
| clientes (customers) | 99.441 | um cliente em um pedido | id do pedido-cliente, id da pessoa, CEP, cidade, estado |
| vendedores (sellers) | 3.095 | um vendedor | CEP, cidade, estado |
| produtos (products) | 32.951 | um produto | categoria, peso, medidas, nº de fotos |
| geolocalização | 1.000.163 | um ponto de CEP | latitude, longitude (19 mil prefixos de CEP) |
| categorias | 71 | uma categoria | nome em português e inglês |

Números de referência: 96.478 pedidos entregues (97%); 96.096 pessoas distintas; recompra de 3,1%; ticket médio por pedido de R$ 161 (mediana R$ 105); cartão em 74% dos pagamentos, média de 3,5 parcelas; 58% de notas 5 e 11,5% de notas 1; prazo mediano de entrega de 10 dias; 6,8% entregues depois do prometido; nota média de 4,29 no prazo contra 2,27 com atraso; 42% dos clientes e 60% dos vendedores em SP.

Cuidados: set a dez/2016 e set a out/2018 têm poucos pedidos (meses incompletos); o cliente real é customer_unique_id; juntar itens e pagamentos na mesma consulta duplica valores; 610 produtos sem categoria.
