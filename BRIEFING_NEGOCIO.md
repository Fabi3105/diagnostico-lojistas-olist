# Briefing do negócio: quem gerou estes dados

Etapa feita **antes** da análise exploratória: entender quem é a empresa, como ela ganha dinheiro e quem é o cliente dela, para não partir de suposições erradas. *(Esta etapa foi acrescentada depois de uma revisão crítica do projeto: a primeira versão tratava o comprador como cliente da Olist, o que distorcia parte das conclusões.)*

## 1. Quem é a Olist

- A Olist conecta **pequenos lojistas** aos **grandes marketplaces** do Brasil (Mercado Livre, Amazon, Americanas, Magalu, Casas Bahia, Carrefour, entre outros). O lojista cadastra o produto uma vez e ele é anunciado nesses canais pela Olist Store.
- O lojista vende **sob a reputação da Olist** nos marketplaces. Nas palavras da própria empresa: "por termos alta reputação nesses sites, nossos lojistas conquistam as melhores posições nos buscadores". Ou seja, a reputação é **coletiva**: o atraso ou o erro de um lojista afeta a posição de todos.
- **Como a Olist ganha dinheiro:** comissão sobre as vendas (que já inclui as taxas de cada marketplace), taxa de adesão e mensalidade por plano. Os percentuais e valores não são públicos e **não estão na base**.

## 2. Quem é o cliente

| Papel | Quem é | O que paga | O que a Olist precisa entregar |
|---|---|---|---|
| **Cliente da Olist** | O **lojista** | Comissão, adesão e mensalidade | Vendas, visibilidade, reputação, logística e ferramentas que facilitem a operação |
| **Comprador** | O cliente do marketplace (e do lojista) | Paga o produto e o frete ao marketplace | Entrega no prazo e produto certo, porque disso depende a reputação de todos |

**Consequências para a análise:**

- A fidelização que importa é a **do lojista** (continuar usando o serviço), não a recompra do comprador. O relacionamento com o comprador é do marketplace.
- O sucesso da Olist é o **sucesso dos lojistas**: vender mais, com boa reputação e pouco atrito. As soluções devem ser **serviços e melhorias para o lojista**, não punições.
- O "faturamento" da base é o **valor bruto vendido pelos lojistas (GMV)**, não a receita da Olist.
- Nota, atraso e cancelamento são **ativos coletivos**: protegem a reputação compartilhada que dá visibilidade a todos os lojistas.

## 3. O que é esta base

- **Amostra:** a própria Olist descreve os dados públicos como **amostrais** ("Perceba que os dados são amostrais"). Não sabemos o critério da amostra, então volumes, crescimento e participações valem **para a amostra**; tendências podem refletir a forma como ela foi feita.
- **Período:** set/2016 a out/2018, cerca de 100 mil pedidos; os meses das pontas são incompletos.
- **Anonimizada:** nomes de empresas nos comentários foram trocados (ex.: "lannister", "stark", "targaryen").
- **Não tem:** comissão, planos, custos, margem, **qual marketplace** originou o pedido, visitas ou carrinhos abandonados, nem a data de entrada e saída do lojista na Olist.
- **Avaliação:** pelos dados, a pesquisa de satisfação é criada cerca de **1 dia após a entrega**, ou cerca de **2 dias após a data prevista** quando o pedido ainda não chegou (verificado nas datas da tabela de avaliações). Por isso, pedido atrasado costuma ser avaliado antes de chegar.

## 3b. Quem controla cada alavanca (a confirmar)

Antes de recomendar uma ação ao lojista, é preciso saber se a alavanca é dele. Com a base e as fontes públicas consultadas, o quadro é:

| Alavanca | Quem controla, pelo que se sabe | Confiança |
|---|---|---|
| Preço, fotos, descrição e categoria do anúncio | O lojista, no cadastro do produto | Alta |
| Prazo de postagem | O lojista (a base registra o limite e a data real de postagem) | Alta |
| Promessa de prazo ao comprador | A plataforma (a base traz a data prometida por pedido) | Alta |
| **Frete cobrado do comprador** | **Não verificado.** Nos marketplaces, o frete costuma ser calculado pelo canal a partir de peso, medidas e distância; o lojista influenciaria pelo peso e pelas medidas declaradas, pelo preço (faixas de frete grátis) e pela localização. A base não diz quem define a tabela nem se o lojista pode subsidiar o frete | Baixa: **pergunta aberta** |
| Transportadora | Não verificado; o estudo assume corresponsabilidade do lojista (decisão registrada no diário) | Baixa |

Consequência: uma recomendação que dependa de uma alavanca de confiança baixa entra no relatório como **hipótese a confirmar com a Olist**, não como ação.

## 4. Perguntas que fazem sentido (e as que não fazem)

- **Fazem:** o que faz o lojista vender mais e continuar na Olist; o que ameaça a reputação coletiva (atraso, erro de envio, cancelamento); onde a logística limita as vendas; quais serviços ajudariam o lojista.
- **Com cuidado:** recompra do comprador (indicador do canal, não da Olist); crescimento ao longo do tempo (pode ser efeito da amostra); qualquer valor em reais de receita ou custo (a base não tem).
- **Não fazem com esta base:** retorno financeiro de ações, margem, comparação entre marketplaces.

## Fontes

- Olist, repositório público do desafio de dados: https://github.com/olist/work-at-olist-data ("os dados são amostrais").
- InfoMoney, captação da Olist (comissão com taxas dos marketplaces, adesão e mensalidade por plano; marketplaces atendidos): https://www.infomoney.com.br/?p=1623965
- Blog da Olist, recursos da Olist Store (reputação compartilhada nos marketplaces): https://olist.com/blog/pt/olist/casos-de-uso/recursos-plataforma-olist-store
- Base: *Brazilian E-Commerce Public Dataset by Olist* (Kaggle), licença CC BY-NC-SA 4.0.
