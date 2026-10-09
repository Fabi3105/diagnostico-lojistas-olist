# Diário de decisões

Registro do que foi perguntado, das decisões de método e do que foi conferido. Cada pergunta tem a consulta em `sql/` e o resultado em `resultados/`.

## Q1. Faturamento por categoria

- **Pergunta (Fabian):** quanto cada categoria fatura?
- **Decisões:** faturamento = soma do preço dos itens, sem frete (o frete é repasse de transporte, não receita do produto). Ficam de fora pedidos cancelados e indisponíveis, que não viraram venda. Produtos sem categoria entram como "sem_categoria".
- **Conferência:** a soma das 74 categorias (R$ 13,49 milhões, 112.101 itens) bate com a soma direta dos itens de pedidos válidos.
- **Resultado:** beleza e saúde lidera (9,3%), seguida de relógios e presentes (8,9%) e cama, mesa e banho (7,7%). Nenhuma categoria passa de 10%; são precisas 18 de 74 categorias para chegar a 80% do faturamento.
- **Revisão do Fabian:** aprovado, com um ajuste: o frete não entra no faturamento de produtos, mas deve aparecer em separado, porque marketplaces como Mercado Livre e Amazon tratam o frete como um negócio próprio. A consulta passou a mostrar frete e total com frete por categoria.

## Q2. Atraso na entrega x nota da avaliação

- **Pergunta (Fabian):** pedido que atrasa reduz a nota da avaliação?
- **Decisões:** só pedidos entregues com data de entrega preenchida e com avaliação (95.824). Comparação por data, sem hora: entregue no dia previsto conta como no prazo. Quando um pedido tem mais de uma avaliação, vale a mais recente.
- **Resultado:** atrasados têm nota média de 2,27 contra 4,29 no prazo; 62% das avaliações de pedidos atrasados são nota 1 ou 2, contra 9% no prazo. A nota cai já com 1 a 3 dias de atraso (3,29) e despenca a partir de 4 dias (2,10). 92% dos pedidos chegam antes da data prevista, sinal de que o prazo informado ao cliente tem folga.
- **Revisão do Fabian:** aprovado sem ajustes.

## Q3. Produtos campeões

- **Pergunta (Fabian):** quais os 5 produtos que mais vendem e o peso deles no total e na categoria?
- **Decisões:** mesmas regras da Q1 (preço sem frete, fora cancelados e indisponíveis). "Mais vendem" foi lido de dois jeitos: por faturamento e por unidades. A base não tem nome de produto; mostramos o código abreviado e a categoria.
- **Resultado:** o maior produto fatura R$ 63,9 mil, 0,47% do total; os 5 maiores somam 1,9%, os 50 maiores 9,3% e os 500 maiores 29,6% de 32.729 produtos vendidos. Os campeões em faturamento são itens caros (até R$ 1.397 por unidade); os campeões em unidades são baratos (R$ 54 a R$ 88), três deles de ferramentas e jardim. Quase todos têm um único vendedor.
- **Revisão do Fabian:** aprovado, com um pedido: verificar se os produtos que vendem em quantidade carregam um frete proporcionalmente maior, por serem de categorias de mais peso físico (feito na Q3b).

## Q3b. Frete x peso x preço (complemento da Q3)

- **Hipótese (Fabian):** os mais vendidos em unidades são de categorias pesadas, e o frete pesa mais no preço deles.
- **Decisões:** frete relativo = soma do frete / soma do preço. Peso do cadastro do produto. "Produtos de volume" = os 100 com mais unidades. Correlação calculada item a item (Pearson e, por postos, Spearman).
- **Resultado:** a hipótese se confirma no efeito e se corrige na causa. Os 100 produtos de volume pagam frete de 19,9% do preço, contra 16,3% dos demais, e os 5 mais vendidos ficam entre 19% e 34%. O peso aumenta o frete em reais (correlação de 0,61), mas quase não muda o frete como % do preço (−0,10). O que define o peso relativo do frete é o preço: itens até R$ 50 pagam frete de 47% do preço; acima de R$ 500, 5% (correlação por postos de −0,81). Os produtos de volume são baratos (R$ 54 a R$ 88), e por isso o frete pesa mais neles.
- **Revisão do Fabian:** aprovado sem ajustes.

## Q4. Os 5 maiores lojistas

- **Pergunta (Fabian):** quem são os 5 maiores lojistas por faturamento?
- **Decisões:** faturamento = preço dos itens do lojista, sem frete (frete ao lado); fora cancelados e indisponíveis. Nota e atraso calculados sobre os pedidos entregues que têm itens do lojista. Categoria principal = a de maior faturamento.
- **Resultado:** os 5 maiores faturam entre R$ 188 mil e R$ 229 mil cada (1,4% a 1,7% do total) e somam 7,7%; os 50 maiores, 33%; os 300 maiores, 67% de 3.053 lojistas. Quatro dos cinco estão em SP e são especializados (75% a 99% numa categoria). Quatro dos cinco atrasam mais que a média da plataforma (9% a 10,5% contra 6,8%), e o 5º colocado tem nota 3,50, abaixo da média de 4,16.
- **Revisão do Fabian:** aprovado sem ajustes.

## Q5. Cancelados e indisponíveis

- **Pergunta (Fabian):** quanto se perde com cancelamentos, em % das vendas?
- **Decisões:** "perdidos" = cancelados + indisponíveis (produto sem estoque), mostrados separados e somados. Valor = soma dos pagamentos (esses pedidos têm pagamento, mas muitos não têm itens). Base = valor pago de todos os pedidos. Etapa do cancelamento deduzida pelas datas preenchidas. Taxa mensal só em meses com 500+ pedidos.
- **Resultado:** 1.234 pedidos perdidos (1,24% dos pedidos e 1,68% do valor, R$ 270 mil); o ticket dos perdidos é maior (R$ 229 cancelados e R$ 208 indisponíveis contra R$ 160). 65% dos cancelamentos acontecem depois do pagamento aprovado e antes do envio, e 100% dos indisponíveis também: a perda nasce no estoque e na expedição do lojista. Os indisponíveis caíram de cerca de 1% dos pedidos em 2017 para perto de 0,1% em meados de 2018. Pedidos pagos com voucher cancelam 2,8%, cerca de 5 vezes os demais. Nenhuma categoria se destaca (0,4% a 1%).
- **Revisão do Fabian:** aprovado, com um pedido: verificar a correlação entre cancelamento e valor do pedido, porque os cancelados parecem ter ticket mais alto que os efetivados (feito na Q5b).

## Q5b. Cancelamento x valor do pedido (complemento da Q5)

- **Hipótese (Fabian):** pedidos de ticket mais alto são os mais cancelados.
- **Decisões:** valor do pedido = soma dos pagamentos; faixas fixas de valor; mediana além da média.
- **Resultado:** a hipótese vale para os pedidos caros, não para o pedido típico. Até R$ 500 a perda fica entre 1,1% e 1,3% em todas as faixas; de R$ 500 a R$ 1.000 sobe para 1,9%; acima de R$ 1.000 chega a 3,75%, três vezes a média. A mediana dos cancelados (R$ 110) é quase igual à das vendas efetivas (R$ 105): a média maior dos cancelados vem de uma cauda de pedidos caros.
- **Revisão do Fabian:** aprovado sem ajustes.

## Q6. Cancelamento x avaliação e atraso

- **Pergunta (Fabian):** existe correlação do cancelamento com as avaliações e com as entregas fora do prazo?
- **Decisões:** avaliação mais recente do pedido. Como quase todo cancelamento acontece antes da entrega, o atraso foi analisado pelo prazo prometido na compra e por lojista (30+ pedidos): quem atrasa mais também cancela mais?
- **Resultado:** com a avaliação a relação é forte: cancelados têm nota 1,80 (70% de notas 1) e indisponíveis 1,53, contra 4,16 dos entregues; pedidos travados em processamento, faturados ou enviados sem chegar têm notas ainda piores (1,26 a 2,00). Com o atraso não há relação: por lojista, a correlação entre taxa de atraso e taxa de cancelamento é 0,07, e os cinco grupos de lojistas, do que menos atrasa ao que mais atrasa, cancelam entre 0,2% e 0,36%, sem tendência. O prazo prometido curto (até 15 dias) tem o dobro de cancelamentos (1,14% contra 0,5% a 0,7%).
- **Revisão do Fabian:** aprovado sem ajustes.

## Q7. Quem recompra avalia melhor?

- **Pergunta (Fabian):** os clientes que recompraram tiveram avaliação melhor?
- **Decisões:** cliente = customer_unique_id; só pedidos efetivos. Recompra = pedido em dia diferente do primeiro: pedidos no mesmo dia contam como uma compra (2.888 pessoas têm mais de um pedido, mas só 2.065 compraram em dias diferentes). Avaliação mais recente do pedido; nota da 1ª compra = média das notas do primeiro dia. Para separar causa e efeito, a análise principal olha a nota e o atraso da 1ª compra e a chance de voltar depois.
- **Resultado:** só 2,2% dos clientes recompraram (2.065 de 94.990). Eles deram nota um pouco melhor na 1ª compra (4,25 contra 4,11) e tiveram menos atraso nela (5,0% contra 6,8%). A chance de voltar sobe com a nota da 1ª compra (1,75% com nota 1, 2,36% com nota 5) e cai quando a 1ª compra atrasa (1,61% contra 2,21%, cerca de 27% menos). A diferença existe, mas é pequena: mesmo quem ficou satisfeito quase nunca volta. Entre os que voltaram, a nota da 2ª compra ficou igual à da 1ª (4,27 contra 4,25).
- **Revisão do Fabian:** aprovado. Pediu que a baixa taxa de recompra entre como achado importante na conclusão, com hipóteses para os motivos. Hipóteses levantadas (não testáveis com esta base): (1) o cliente compra na vitrine do parceiro e não sabe que a Olist está por trás, então não cria vínculo; (2) não há programa de fidelidade nem comunicação pós-venda própria; (3) o mix é de compras pouco recorrentes (móveis, relógios, presentes, utilidades), que não se repetem em meses; (4) a base cobre só cerca de 2 anos, curto para recompra de bens duráveis; (5) o cliente pode voltar ao mesmo lojista fora da Olist ou por outra plataforma.

## Q8. Estados: população x tempo de entrega

- **Pergunta (Fabian):** estados com mais gente compram mais por terem mais gente, ou alguns compram mais por causa do tempo de entrega?
- **Fonte externa:** população estimada 2017 por UF (IBGE, SIDRA tabela 6579), total de 207.660.929, em `dados/externos/populacao_uf_2017.csv`.
- **Decisões:** estado do cliente; cliente = customer_unique_id; pedidos efetivos. Intensidade = compradores por 100 mil habitantes, que tira o efeito do tamanho. Prazo real = mediana de dias da compra à entrega. Correlações por postos (Spearman) entre os 27 estados.
- **Resultado:** as duas coisas valem, para medidas diferentes. O número absoluto de compradores acompanha a população (correlação de 0,95). Mas a intensidade (quantos compram a cada 100 mil) acompanha o prazo de entrega muito mais do que a população: correlação de −0,95 com o prazo real e de −0,82 com o peso do frete, contra 0,53 com a população. SP tem 88 compradores por 100 mil e entrega em 7 dias; o Amazonas, 3,5 por 100 mil e 26 dias. SP é 21,7% da população e 38,3% do faturamento. Ressalva: prazo, frete e renda andam juntos (os estados longe de SP são também os de menor renda), e a base não permite separar esses efeitos.
- **Revisão do Fabian:** pediu para incluir a renda por estado, para avaliar se vale mais investir em atrair lojistas em outras regiões ou em logística própria para reduzir o prazo (feito na Q8b).

## Q8b. Renda x prazo de entrega

- **Pergunta (Fabian):** separar o efeito da renda do efeito do prazo, para orientar investimento em lojistas regionais ou logística própria.
- **Fonte externa:** rendimento domiciliar per capita 2017 por UF (IBGE, PNAD Contínua, SIDRA tabela 7531).
- **Decisões:** modelo linear nos 27 estados: ln(compradores por 100 mil) explicado por ln(renda) e prazo real mediano. Cenário de prazo de 7 dias (o de SP) mantendo a renda de cada estado.
- **Resultado:** renda e prazo explicam juntos 90% da diferença de intensidade entre estados (só renda: 67%; só prazo: 84%). Os dois pesam, mas o prazo pesa mais: descontada a renda, a correlação do prazo com a intensidade continua em −0,84; descontado o prazo, a da renda cai para 0,62. Pelo modelo, cada dia a menos de prazo se associa a 12% mais compradores por habitante, e 10% a mais de renda a 8%. No cenário de prazo de 7 dias, a base teria cerca de 50 mil compradores a mais (+53%), com maior ganho no Nordeste (18,8 mil), no Sul (11,3 mil) e no Centro-Oeste (7,3 mil); por estado, RS, BA e PR lideram. Ressalvas: renda e prazo são correlacionados (−0,70), o modelo compara estados e não mede causa, e não considera custos.
- **Revisão do Fabian:** aprovado sem ajustes (Q8b e Q9). Recomendações dele registradas em CONCLUSOES.md.

## Q9. Faturamento mês a mês por ano

- **Pergunta (Fabian):** fluxo de compras ao longo dos meses comparando ano a ano, uma linha por ano.
- **Decisões:** faturamento = preço dos itens de pedidos efetivos, pela data da compra; frete ao lado. 2016 só tem outubro relevante; set e out/2018 (20 pedidos) ficam de fora. Comparação justa: jan a ago de 2017 x 2018.
- **Resultado:** de jan a ago, o faturamento passou de R$ 3,08 milhões (2017) para R$ 7,34 milhões (2018), +138%, com pedidos de 22,6 mil para 53,5 mil. Mas o crescimento perdeu força: 2017 subiu quase todo mês até o pico da Black Friday (R$ 1,00 milhão em nov); em 2018 o faturamento ficou estável entre R$ 840 mil e R$ 990 mil por mês, e a alta sobre o mesmo mês do ano anterior caiu de +687% em janeiro para +49% em agosto. Ticket médio estável, entre R$ 125 e R$ 150.
- **Revisão do Fabian:** aprovado sem ajustes (Q8b e Q9). Recomendações dele registradas em CONCLUSOES.md.

## Q10. Black Friday 2017

- **Pergunta (Fabian):** quanto as vendas sobem na Black Friday, quais categorias mais vendem e qual o impacto no atraso e nas avaliações?
- **Decisões:** só a BF de 2017 está na base. Períodos: antes = 01/10 a 19/11/2017 (50 dias); semana da BF = 20 a 26/11 (7 dias); pós-BF = 27/11 a 31/12. Comparação por dia, porque os períodos têm tamanhos diferentes. Pedidos efetivos; atraso e nota de pedidos entregues.
- **Resultado:** na sexta, 24/11, foram 1.166 pedidos, cerca de 7 vezes um dia normal; na semana, 2,8 vezes mais pedidos por dia e 2,65 vezes mais faturamento por dia, com ticket um pouco menor (R$ 136 contra R$ 143). O prazo prometido não mudou (23 dias), mas a operação não deu conta: o atraso subiu de 4,9% para 17,3% e a nota média caiu de 4,19 para 3,85; no pós-BF o atraso ainda ficou em 9,2%. Cama, mesa e banho passou a liderar; perfumaria, móveis e decoração, beleza e saúde e cama, mesa e banho cresceram 3,4 a 3,8 vezes, enquanto esporte e lazer e cool stuff cresceram menos de 2 vezes.
- **Revisão do Fabian:** aprovado. Aumentar o prazo prometido na semana da BF faz sentido, por ser um período de valores menores. Exigir estoque dos lojistas não faz sentido: eles também são clientes da plataforma, e não cabe impor esse tipo de exigência sobre a operação deles (recomendação descartada). A BF é o período ideal para a fidelização: além de pagar mais barato, o cliente ganha desconto ou cashback para a próxima compra, o que aumenta o retorno desses clientes sazonais. Retomar na conclusão.

## A. Onde nasce o atraso (sugestão do Claude)

- **Pergunta:** o atraso nasce na aprovação do pagamento, na postagem pelo lojista ou no transporte? Ligada à Q2, Q4, Q8 e Q10.
- **Decisões:** pedidos entregues com as três datas. Etapas em dias: aprovação (compra até pagamento aprovado), postagem (aprovado até entregue à transportadora), transporte (transportadora até cliente). Excluídos 1.373 pedidos (1,4%) com etapa negativa, erro de registro. Atrasado como na Q2. Postagem fora do limite = depois do prazo de envio dado ao lojista (shipping_limit_date).
- **Resultado:** o atraso nasce principalmente no transporte. O pedido atrasado leva em média 22,9 dias a mais; 86,8% desse excesso está no transporte (mediana de 26,2 dias contra 7,0), 12,8% na postagem e 0,5% na aprovação. O lojista ainda pesa: quem posta fora do limite (9,1% dos pedidos) tem atraso de 20,9%, contra 5,4% de quem posta no limite, e 28% dos atrasados tiveram postagem fora. Por região, a postagem é igual em todas (1,8 a 1,9 dia); a diferença está no transporte (SE 6,0 dias, NE 14,0, N 16,4), e o Nordeste tem o maior atraso (12,8%) mesmo com prazo prometido de 31 dias. Lojista no mesmo estado do cliente: transporte de 3,7 dias e atraso de 4,6%, contra 9,2 dias e 8,1%. Na BF, as duas etapas pioraram: postagem fora do limite de 8,7% para 15,3% e transporte de 7,1 para 9,9 dias. Entre os 5 maiores lojistas, o Lojista 5 posta fora do limite em 29,8% dos pedidos (mediana de 11 dias para postar); os demais atrasam por transporte. A nota do atrasado é 2,27 seja qual for a causa: para o cliente, quem atrasou é a plataforma.
- **Revisão do Fabian:** aprovado sem ajustes. Pediu para levar os achados ao resumo de conclusões.

## B. Peso do frete por estado (sugestão do Claude)

- **Pergunta:** quanto o frete pesa para o cliente de cada estado e o que isso explica? Ligada à Q1, Q3b, Q8, A e Q2.
- **Decisões:** itens de pedidos efetivos, estado do cliente. Como o preço do item define o peso do frete (Q3b), a comparação justa entre estados usa a mesma faixa de preço (itens de R$ 50 a R$ 100). Nota x frete só em pedidos entregues no prazo, para tirar o efeito do atraso. Correlações por estado (Spearman).
- **Resultado:** o frete médio por item vai de R$ 17 no Sudeste a R$ 37 no Norte. No percentual geral a diferença parece menor (15% contra 23%) porque Norte e Nordeste compram itens mais caros; na mesma faixa de R$ 50 a R$ 100, o frete é 21% do preço no Sudeste, 37% no Nordeste e 41% no Norte, e num item de até R$ 50 chega a 84% no Norte. Norte e Nordeste compram menos itens baratos (29% contra 36% dos itens), compatível com o frete inibindo a compra pequena. Norte e Nordeste pagam 18,3% de todo o frete com 13,9% do faturamento. Por estado, o frete na mesma faixa acompanha a intensidade de compra da Q8 (−0,86), mas também o transporte (0,83): frete e prazo vêm juntos da distância e a base não separa os dois. Lojista no mesmo estado: frete de R$ 13,45 por item contra R$ 23,69, e 17% contra 27% na faixa de R$ 50 a R$ 100. Nos pedidos entregues no prazo, a nota quase não muda com o peso do frete (4,34 com até 10%; 4,25 com mais de 50%; correlação −0,03): o frete atua antes da compra, o atraso depois.
- **Revisão do Fabian:** aprovado sem ajustes. Pediu para salvar os insights no resumo de conclusões.

## C. Temas dos comentários de nota 1, classificados com IA (sugestão do Claude)

- **Pergunta:** do que reclama quem dá nota 1? Ligada à Q2, Q5/Q6, Q8/B, Q10 e A.
- **Decisões:** avaliação mais recente por pedido; 8.706 comentários de nota 1 (os 2.657 sem texto ficam de fora). Claude definiu 10 temas a partir de uma amostra; 9 agentes do Claude classificaram todos os comentários um a um (tema principal + "sem resposta"). Validação manual de 100 rótulos aleatórios: cerca de 95 concordantes. Cinco grupos: Logística, Lojista, Produto, Atendimento, Outro. Publicar só ids e rótulos, nunca os textos.
- **Resultado:** Logística 42,5% (não recebido 34,2%, falha na entrega 4,5%, atraso 3,8%), Lojista 31,9% (incompleto 16,1%, produto errado 10,6%, cancelamento/estoque 5,2%), Produto 18,3% (qualidade/anúncio 10,5%, defeito 7,8%), Atendimento 1,9%. Em 83% dos "não recebido" a avaliação foi feita antes da entrega, e 72% desses pedidos acabaram entregues (58% com atraso): é o atraso da Q2/A visto pelo cliente. "Incompleto": 82% são pedidos com mais de um item (contra 10% na base) e 20% com mais de um lojista (contra 1,3%): em boa parte, pedido entregue em partes. Metade do "cancelamento/estoque" é de pedido cancelado ou indisponível (Q5). O Nordeste tem 54% de reclamações logísticas, contra 41,5% no Sudeste (B/A). Os comentários logísticos disparam nos picos operacionais: Black Friday (51% em nov/2017, Q10) e fev-mar/2018 (57-58%, quando o atraso foi de 14% e 19%). 11,8% citam falta de resposta da loja ou da plataforma.
- **Revisão do Fabian:** aprovado sem ajustes. Pediu para levar os insights ao resumo de conclusões.

## D. Lojistas que prejudicam a plataforma (sugestão do Claude)

- **Pergunta:** existem lojistas que geram muito mais insatisfação que os outros? Quanto pesam e por quê? Ligada à Q2, Q4, Q6, A e C.
- **Decisões:** só lojistas com 30 ou mais pedidos avaliados (628 de 3.095, 77% do faturamento). "Prejudica" = taxa de nota 1 de pelo menos 1,5 vez a da plataforma (11,4%) e estatisticamente acima do esperado (z ≥ 2). Excesso = notas 1 além do esperado para o volume. Causas: postagem fora do limite ou atraso no dobro da média; reclamações de separação/estoque ou de produto (temas da C) em 3% ou mais dos pedidos.
- **Resultado:** 46 lojistas prejudicam: taxa de nota 1 de 24,5% contra 10,2% dos demais, nota média 3,46 contra 4,13. Fazem 5,6% dos pedidos e 6,0% do faturamento, mas 12,0% das notas 1; o excesso é de 727 notas 1 (6,4% de todas). Não são pequenos: faturamento mediano de R$ 9,1 mil, contra R$ 7,8 mil dos demais. Perfil: postam fora do limite 3 vezes mais (22,7% contra 7,7%), atrasam mais (11,3% contra 6,4%), têm 2,5 vezes mais reclamações de separação/estoque e 3,9 vezes mais de produto. As causas se acumulam: separação/estoque em 36 dos 46, produto em 30, postagem em 29, atraso em 20. O maior deles é o Lojista 5 da Q4 e da A (R$ 188 mil, 20% de nota 1, postagem fora em 30%). Cancelamento não diferencia (0,48% contra 0,28%), coerente com a Q6. Se os 46 tivessem a nota dos demais, a nota da plataforma iria de 4,09 para 4,13: o problema é concentrado, mas a maior parte da nota 1 é estrutural (logística, C).
- **Revisão do Fabian:** aprovado. Aprovou as três ações (mostrar indicadores e reclamações ao lojista, alerta de prazo de postagem, redução de exposição só para quem não melhora) e acrescentou uma campanha de comissionamento: lojista bem avaliado ganha vantagens além da exposição, como redução percentual na comissão; avaliação por lojista, não por compra; incentivo a transportadoras mais eficientes e, no futuro, transportadora própria do marketplace. Registrado como recomendação 4 em CONCLUSOES.md.

## Relatório (revisão do Fabian)

- Ajustes pedidos no relatório: retirar a menção à empresa do autor; reescrever o achado de renda x prazo (Q8b); explicitar a referência das comparações entre parênteses; centros logísticos de *last mile*.
- Comissionamento (recomendação 4): o atraso de transporte deve contar na nota do lojista, porque a transportadora é escolha dele e ele é corresponsável pelo prazo; se oferece várias transportadoras, deve eliminar as que não cumprem os prazos. Isentá-lo geraria inércia. Mantido o volume mínimo de avaliações para a nota valer na comissão.
- Repositório: só os arquivos necessários para reproduzir e entender a análise; os scripts Python das perguntas Q8b e A a D foram reunidos em `scripts/` e conferidos (geram os mesmos resultados).

## Revisão crítica do projeto (decisões do Fabian)

- **Modelo de negócio:** o cliente da Olist é o **lojista** (paga comissão, adesão e mensalidade); o comprador é cliente do marketplace. A fidelização que importa é a do lojista. As soluções devem ser melhorias e serviços para o lojista, não punições. Criado o `BRIEFING_NEGOCIO.md`, etapa que passa a vir antes da análise exploratória (e fará parte da skill de análise a ser criada no fim do projeto).
- **Dimensionamento:** sem dados de custo, não estimar valores. O relatório é de **direcionamento**, não de aplicação direta; cada solução deve ser estudada individualmente. Ordenar as soluções do menor ao maior custo operacional, separando custo financeiro e custo humano, para priorizar os estudos.
- **Recompra:** padrão de até 90 dias após a compra anterior.
- **Amostra:** mencionar onde for pertinente que a base é amostral.
- **Prazo prometido x real:** medir quanto o prazo de vitrine pode ser reduzido sem derrubar as avaliações.
- **Extrapolações:** apresentar com margem de erro e por faixas.
- **Validação da IA:** aplicar o índice kappa com uma amostra classificada pelo Fabian.
- **Método:** descrever como foi realmente feito (decisões do Fabian, execução com apoio de IA), sem afirmar o que não foi feito.
- **Painel:** filtros no HTML; o Power BI deixa de ser necessário.

## E. Retenção dos lojistas (sugestão do Claude, após o reenquadramento)

- **Pergunta:** o lojista, cliente da Olist, continua vendendo? O que diferencia quem fica de quem para?
- **Decisões:** a base não tem a data de saída do lojista; indicador aproximado: "inativo" = sem venda nos últimos 90 dias da base (referência 01/09/2018). Universo: 2.072 lojistas com primeira venda até fev/2018. Como a base é amostral, calculada para cada lojista a chance de 90 dias sem venda só por acaso (distribuição de Poisson, pelo ritmo de vendas dele antes do período final). Métricas dos primeiros 90 dias de cada lojista, para olhar o começo da relação e evitar causa invertida. Execução em Python (`scripts/qE_retencao_lojistas.py`).
- **Resultado:** os lojistas ativos por mês passaram de 773 (out/2017) para 1.266 (ago/2018), +64%, enquanto o GMV ficou estável: o GMV por lojista ativo caiu de R$ 988 (mar/2018) para R$ 671 (ago/2018), −32%, e os pedidos por lojista de 7,2 para 5,1. 54,7% dos lojistas estavam inativos; o acaso da amostra explicaria 22,3%, então cerca de 32 pontos indicam saída real. O fator mais forte é vender pouco no começo: com 1 venda nos primeiros 90 dias, 80% ficaram inativos (acaso: 54%); com 10 ou mais, 24% (acaso: 0,3%). Entre lojistas com volume parecido (5+ vendas no início), atraso e postagem não diferenciam quem para; só nota média abaixo de 3 (51% inativos contra 30 a 37%, com apenas 39 lojistas). Ressalvas: indicador aproximado de saída; base amostral; associação, não causa.
- **Revisão do Fabian:** aprovado sem ajustes.

## F. Segmentação RFM dos lojistas (sugestão do Claude)

- **Pergunta:** em que situação está cada lojista (cliente da Olist), e onde agir primeiro?
- **Decisões:** RFM = Recência (dias desde a última venda, referência 01/09/2018), Frequência (pedidos efetivos) e Valor (GMV). Faixas fixas e explicáveis em vez de quintis (com muitos empates, quintis separariam lojistas iguais). Sete segmentos: Campeões, Em crescimento, Esfriando, Novos, Ativos de baixo volume, Em risco e Inativos (definições em `scripts/qF_rfm_lojistas.py`). GMV total e dos últimos 90 dias. Base amostral: silêncio de lojista pequeno pode ser acaso (E).
- **Resultado:** 451 Campeões (15% dos lojistas) fazem 62% do GMV total e 65% do GMV dos últimos 90 dias. Esfriando (197) e Em risco (127) somam 324 lojistas e 17% do GMV histórico, mas só 4,6% do GMV recente: é o grupo para ação de retenção. Novos são 468 (15%), com 8,5% do GMV recente: grupo para ativação (E). Inativos são 1.129 (37%), com mediana de 2 pedidos e qualidade pior (nota 3,81; 19% de notas 1; postagem fora do limite 17,5%). Dos 46 lojistas que prejudicam a reputação (D), 28 são Campeões: são grandes e a plataforma depende deles.
- **Revisão do Fabian:** aprovado sem ajustes.

## G. Prazo prometido x prazo real (sugestão do Claude, levantada na revisão crítica)

- **Pergunta (Fabian):** comparando o prometido com o entregue, quanto dá para reduzir o prazo de vitrine sem derrubar as avaliações?
- **Decisões:** nota esperada de cada pedido pela curva observada "nota média x dias entre entrega e data prometida"; hipótese: o cliente reagiria a um novo atraso como reagem os atrasados de hoje. Duas políticas: (a) corte uniforme de k dias; (b) promessa por rota (estado do lojista → estado do cliente) igual a um percentil do prazo real, aprendida nos pedidos de 2017 e testada nos de 2018 (para não testar com os mesmos dados que geraram a regra). Margem de erro de 95% por reamostragem (bootstrap), que não inclui a incerteza da hipótese. Execução em Python (`scripts/qG_prazo_prometido.py`).
- **Resultado:** hoje o prazo prometido mediano é de 24 dias e o real de 10; o pedido chega em média 12 dias antes. Chegar muito antes quase não melhora a nota (4,37 com 20 dias de antecedência, 4,12 com 3), mas 1 dia de atraso já derruba para 3,73 e 3 dias para 2,68. Corte uniforme: 2 dias a menos levariam o atraso de 6,7% para 9,6% e a nota de 4,15 para 4,10; 4 dias, para 13% e 4,02. Promessa por rota (percentil 93, testada em 2018): prazo mediano de 23 para 21 dias, com atraso de 7,8% para 7,5% e nota esperada de 4,13 para 4,15 (margem de ±0,005). Por região: Sudeste de 21 para 17 dias sem perder nota; Sul e Centro-Oeste 2 dias a menos; Nordeste com promessa 5 dias maior (29 para 34), mas atraso de 14,4% para 7,3% e nota de 3,98 para 4,14. A promessa atual é longa demais onde a entrega é rápida e curta demais onde é lenta.
- **Revisão do Fabian:** aprovado sem ajustes.

## Revisões após a crítica (recompra, Q8b, sensibilidade da D)

- **Recompra em 90 dias (Q7 revisada, decisão do Fabian):** nova compra em outro dia até 90 dias depois da primeira, só com clientes que tiveram os 90 dias completos na base (77.339). Resultado: 1,31% (contra 2,2% no cálculo antigo, sem janela). Em 180 dias, 1,99%. A mediana até a segunda compra é de 74 dias, então a janela de 90 dias captura pouco mais da metade das recompras. Taxa estável entre as coortes (1,1% a 1,6%). `scripts/q07b_recompra_90d.py`.
- **Q8b com margem de erro:** intervalos de 95% por reamostragem dos 27 estados (bootstrap). Cada dia a menos de prazo: +12,1% de compradores por habitante (de 8,4% a 15,9%). Cenários por faixa, mantendo a renda: 2 dias a menos em cada estado, +14 mil compradores (de 10 mil a 19 mil, +15%); 4 dias a menos, +29 mil (de 19 mil a 41 mil, +31%); prazo de SP em todos, +61 mil (de 37 mil a 93 mil, +64%). O cálculo foi corrigido: o anterior (50 mil) somava ao efeito do prazo a diferença entre o modelo e o observado de cada estado. São extrapolações de uma comparação entre 27 estados, não efeito causal medido, e o prazo levado para cada faixa depende de investimento que a base não mostra.
- **Sensibilidade da D:** refeita com 27 combinações de critérios (mínimo de 20, 30 ou 50 avaliações; 1,3, 1,5 ou 2 vezes a taxa de nota 1; z de 1,5, 2 ou 2,5). O tamanho do grupo varia muito (17 a 95 lojistas, 1,7% a 10,5% do GMV), mas o padrão se mantém em todas: o grupo concentra de 1,8 a 2,9 vezes mais notas 1 do que vendas, tem taxa de nota 1 de 21% a 32% (contra cerca de 10% dos demais) e postagem fora do limite de 17% a 34% (contra 7,7%). `resultados/qD_lojistas_problema_4_sensibilidade.csv`.
- **Revisão do Fabian:** aprovado sem ajustes.

## Validação da classificação com IA, parte 1: consistência entre IAs (decisão do Fabian)

- **Pergunta (Fabian):** acrescentar mais duas classificações independentes por IA aumenta a validação, já que modelos generativos podem interpretar o mesmo texto de formas diferentes?
- **Decisões:** amostra de 1.000 comentários, incluindo os 150 da planilha de validação humana. Duas novas classificações independentes, sem acesso aos rótulos anteriores: B com outro modelo (Claude Opus) e C com o mesmo modelo da original (Claude Sonnet), ambas com as mesmas regras e temas, mas com instruções redigidas de outra forma. Concordância medida pelo kappa de Cohen (pares) e pelo kappa de Fleiss (os três). Ressalva registrada: IAs do mesmo tipo tendem a errar nos mesmos casos; a concordância entre elas mede consistência, não acerto. A medida de acerto virá da comparação com a classificação do Fabian. `scripts/qC_validacao_ia.py`.
- **Resultado:** concordância muito alta. Por tema: 94,6% a 95,7% entre pares (kappa de 0,93 a 0,95); os três iguais em 92,8% dos casos (kappa de Fleiss 0,94). Por grupo (logística, lojista, produto, outros): 96,4% com os três iguais (kappa 0,96). Marcação de "sem resposta": kappa de 0,83 a 0,87. Só 2 comentários ficaram sem maioria. As divergências se concentram entre temas vizinhos: "não recebido" com "falha na entrega" e "atraso" (todos de logística) e "atendimento" (o tema menos estável, 79% de concordância com o validador B). A distribuição dos temas é praticamente igual nas três classificações (ex.: "não recebido" 37,2%, 36,0% e 36,6%).
- **Revisão do Fabian:** concluída com a validação humana (parte 2, abaixo); aprovado em 09/10/2026.

## Painel (index.html) na perspectiva do lojista, com filtros

- **Decisão do Fabian:** painel em HTML com filtros, no lugar do Power BI.
- **Decisões:** filtros de período (mês inicial e final), região e estado do comprador e categoria (15 maiores e demais). Cada gráfico indica se responde aos filtros ou se é fixo (resultado de uma análise feita sobre a base completa, como retenção, grupos de lojistas, promessa ajustada e cenários). Base do painel: um resumo por mês, estado e categoria (`scripts/painel_dados.py`), montado no modelo `scripts/painel_modelo.html` por `scripts/painel_montar.py`. Pedidos efetivos de jan/2017 a ago/2018. No mapa, a intensidade passou a ser "pedidos por 100 mil habitantes", porque compradores distintos não podem ser somados entre filtros.
- **Revisão do Fabian:** aprovado em 09/10/2026, junto com a aprovação do relatório final.

## Validação da classificação com IA, parte 2: comparação com a classificação humana

- **Decisões:** Fabian classificou 150 comentários sorteados (149 válidos; 1 ficou em branco), sem ver os rótulos da IA, seguindo as mesmas regras. Comparação pelo kappa de Cohen por tema, por grupo e com "não recebido" e "atraso" fundidos. A marcação "sem resposta" não foi preenchida e ficou fora da comparação. `scripts/qC_validacao_humana.py`; rótulos do Fabian (sem os textos) em `resultados/qC_validacao_rotulos_fabian.csv`.
- **Resultado:** por tema, a concordância entre Fabian e a IA foi de 63% a 65% (kappa de 0,57 a 0,60, moderada), bem abaixo da concordância entre as IAs (95%). A maior parte da diferença está em uma interpretação: em 24 dos 55 desacordos, Fabian classificou como "atraso" comentários de pedidos ainda não recebidos com prazo vencido, que a regra mandava classificar como "não recebido". Fundindo esses dois temas, a concordância sobe para 79% a 80% (kappa de 0,73 a 0,74, boa). Por grupo, a concordância é de 83% a 85% (kappa de 0,75 a 0,77, boa). Os demais desacordos são casos de fronteira (cancelamento com reclamação de atendimento; falsificado como "produto errado" ou "qualidade"). A distribuição por grupo é parecida: entrega 43% (Fabian) contra 47% (IA), erro de envio ou estoque 32% e 32%, produto 16% e 14%, outros 9% e 7%.
- **Conclusão:** as conclusões por grupo se sustentam (entrega e erro de envio somam 75% na leitura do Fabian e 79% na da IA). A divisão fina dentro da entrega (não recebido x atraso) depende da definição e não deve ser usada isoladamente. A alta concordância entre as IAs mostra consistência, e a comparação humana mostra que parte das diferenças vem das regras, não de erros de leitura: fica como aprendizado deixar as definições de temas vizinhos mais explícitas.
- **Revisão do Fabian:** aprovado em 09/10/2026, junto com a aprovação do relatório final.

## Revisão final como analista sênior de varejo (nota 8,0) e melhorias 1 a 9

- **Pedido do Fabian:** revisão crítica do relatório com nota de 0 a 10; aprovou implementar as nove melhorias sugeridas.
- **1. Diagnóstico da ativação (análise H, nova):** 2.392 lojistas com primeira venda de jan/2017 a mai/2018; "deslanchou" = 5 ou mais pedidos efetivos nos primeiros 90 dias (47%). Regressão logística (NumPy, sem bibliotecas extras), efeitos em pontos percentuais com os demais fatores fixos e margem de 90% por bootstrap (500 reamostragens). Refeita com 3+, 10+ pedidos e valor acima da mediana. Resultados que se mantêm: frete acima de 40% do preço (−13 pontos), descrição com até 300 caracteres (−18), categorias (cama, mesa e banho +15; móveis e decoração −15). Primeira venda com nota 1 ou 2: −8. Fotos e preço não se sustentam (o preço inverte o sinal quando o critério é valor) e ficaram fora das conclusões. Número de produtos não foi usado: a base só tem produtos que venderam. Cenário para meta: sem frete acima de 40% e sem descrição curta, 47% → 52%. `scripts/qH_ativacao_lojistas.py`.
- **2. Padronização:** período padrão jan/2017 a ago/2018, pedidos efetivos, tempos em mediana, notas em média (`base.pedidos_padrao`). `scripts/indicadores_padrao.py` gera os valores gerais, iguais aos do painel sem filtros (verificado: GMV R$ 13,45 mi, atraso 6,8%, nota 4,12, notas 1 10,7%, postagem fora 9,0%, prazo 24 x 10 dias, etapas por região). O painel passou a calcular medianas com histogramas por célula. Temas das notas 1 no período padrão incluem pedidos cancelados (8.613 comentários). Dicionário de indicadores acrescentado ao relatório, com as análises que usam base própria.
- **3. Frases causais:** "o lojista sai porque não vende" trocado por "o volume inicial é o sinal mais forte de saída", com a ressalva da direção.
- **4. Troca no Nordeste:** promessa mais longa pode reduzir a conversão; mudança proposta como piloto, medindo conversão, atraso e nota.
- **5. Metas:** tabela de indicadores com meta inicial, base da meta, frequência e área responsável. Onde a base não dá referência, a meta fica para o piloto.
- **6. Decisão no sumário:** três pilotos para 90 dias (soluções 1, 2 e 7), com as soluções 3 e 4 em paralelo.
- **7. Sensibilidade da inatividade:** 60, 90 e 180 dias; saída real acima do acaso de 29, 32 e 34 pontos; o padrão por volume inicial se mantém. `resultados/qE_retencao_lojistas_5.csv`.
- **8. Vendas (análise I, nova):** ticket médio estável (R$ 125 a R$ 153; 1,1 item por pedido): a estagnação de 2018 vem do número de pedidos. Jan-ago/2018 x jan-ago/2017: venda por lojista +23% no total, mas −43% em perfumaria, −40% em brinquedos, −18% em cool stuff e −9% em cama, mesa e banho (lojistas cresceram mais que as vendas). Lojistas estreantes de 2018 fizeram 30% das vendas de jan-ago/2018. `scripts/qI_vendas_categorias.py`.
- **9. Termos:** gráfico de vendas renomeado (g1_vendas_mensais.png); margem de 8% a 16% no sumário. Correção encontrada na revisão: o texto dizia que as vendas "ficaram estáveis" de out/2017 a ago/2018, mas subiram 29% nesse intervalo; o trecho passou a usar mar-ago/2018 para lojistas (+27%), vendas (−13%) e vendas por lojista (−32%).
- **Revisão do Fabian:** aprovado em 09/10/2026, junto com a aprovação do relatório final.

## Ajustes após a revisão final (decisões do Fabian)

- **Anexos:** o dicionário de indicadores (Anexo A) e a referência das análises e arquivos (Anexo B) saíram do corpo do relatório; o PDF passou a 16 páginas.
- **Metas sem apoio nos dados ficam em aberto:** a tabela de indicadores ganhou a coluna "Apoio nos dados". Só três metas têm apoio direto (ativação 47% → 52%, pelo modelo; atraso no Nordeste até 8% e promessa no Sudeste de 17 dias, pela simulação). As outras ficaram "em aberto", com a explicação do que falta (custos, histórico de ações, conversão). Regra registrada para a skill: o que não tem apoio em dados fica em aberto, com a razão explícita.
- **Correção de forma:** tabelas longas passaram a quebrar entre páginas com o cabeçalho repetido, em vez de pular para a página seguinte deixando espaço vazio.
- **Revisão do Fabian:** aprovado em 09/10/2026, junto com a aprovação do relatório final.

## Reanálise do projeto inteiro (nota 8,3) e melhorias 1 a 8 (decisão do Fabian: implementar tudo e manter a pasta limpa)

- **1. Reprodução:** `README.md`, `requirements.txt` e `scripts/rodar_tudo.py` (roda validação, SQL, análises, indicadores, gráficos, painel e conferência, na ordem; aceita retomar de um ponto). `scripts/rodar_sql.py` executa as consultas de `sql/` no DuckDB ou, traduzindo as poucas funções de dialeto, no SQLite; os CSVs de Q1 a Q10 foram regerados por ele e conferidos contra os anteriores (37 arquivos idênticos; 4 só perderam colunas que vinham de cálculo fora do SQL, como a correlação de Spearman, não usadas no relatório). A variável `OLIST_SQLITE` ficou documentada em `base.py` e no README.
- **Pasta limpa (decisão do Fabian):** só fica o que foi usado. Saíram de `sql/` as versões SQL de A, B e D, que nunca geraram resultado (a execução foi em Python) e o `rodar_sql.py` antigo só para DuckDB; os arquivos de método (`q08b_renda_prazo.md`, `qC_*.md`) foram para a pasta `metodo/`. O que saiu está em `_lixo/`, fora do Git.
- **2. Conferência automática:** `scripts/conferir_relatorio.py` lê 68 números-chave dos CSVs, formata como o relatório escreve e procura o texto no RELATORIO.md (`resultados/conferencia_relatorio.csv`). Os 68 batem.
- **3. Validação da base:** `scripts/validar_dados.py`, 45 checagens (tamanhos, chaves, órfãos, datas, nulos, valores), todas com observação do tratamento dado (`resultados/validacao_dados.csv`). Nenhuma falha; 1.359 pedidos com data de transportadora antes da aprovação e 23 com entrega antes da transportadora ficam fora das etapas de entrega.
- **4. Quem controla o frete:** o briefing ganhou a seção 3b (quem controla cada alavanca, com grau de confiança). O frete cobrado do comprador é pergunta aberta: nos marketplaces costuma ser calculado pelo canal por peso, medidas e distância. O relatório passou a tratar a revisão do frete como condicional ("se o lojista controlar o frete") e a meta de ativação ficou 47% → 50% só com a descrição, 52% se o frete também for controlável. Regra para a skill: toda recomendação passa por "quem controla essa alavanca?".
- **5. Safras e sobrevivência (análise J):** 66% dos lojistas ainda vendem após 3 meses, 56% após 6, 47% após 9 e 42% após 12; safras de 2017 parecidas entre si (55% a 64% após 6 meses). Quem fez 5+ vendas nos primeiros 90 dias: 76% após 6 meses e 63% após 12; os demais, 38% e 23%. Só entram, em cada ponto, lojistas com aquele tempo de observação. `scripts/qJ_safras_lojistas.py`, gráfico g14.
- **6. Estabilidade da amostra (análise K):** ticket, entregues e avaliados estáveis mês a mês (desvio relativo até 5%), mas a participação de SP entre compradores sobe de 37% para 50% entre jan/2017 e ago/2018. Pode ser crescimento real ou efeito da amostra; o relatório passou a recomendar leitura por região das tendências de prazo e frete. `scripts/qK_estabilidade_amostra.py`.
- **7. Tabelas não usadas:** geolocalização (distância em km) e pagamentos ficaram fora por decisão de escopo; registrado na seção "Método" como extensão possível.
- **8. Entradas pendentes:** fechadas com a aprovação do relatório em 09/10/2026.
- **Revisão do Fabian:** aprovado em 09/10/2026, junto com a aprovação do relatório final.

## Revisão de escrita e encerramento (decisão do Fabian)

- **Relatório aprovado.** Pedido final: escrita formal e direta, plenamente inteligível para gestores e diretoria.
- **Revisão de escrita:** termos técnicos explicados na primeira ocorrência (mediana, pontos, conversão, bootstrap, RFM, última milha); "safras" acompanhado de "turmas de entrada"; "estagnação" e "demanda" trocados por palavras do dia a dia onde não perdiam precisão; frases longas divididas. Os 68 números-chave continuam batendo com os CSVs (`conferir_relatorio.py`).
- **Pendências:** todas as entradas marcadas "(pendente)" foram fechadas como aprovadas na data do relatório.
- **Próximo passo:** criação da skill de análise de dados a partir deste projeto, com melhoria contínua: ao fim de cada análise, a skill é revisada com o que se aprendeu.
