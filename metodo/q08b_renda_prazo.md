# Q8b. Renda x prazo de entrega por estado (método)

Esta etapa é um modelo estatístico simples, feito em Python (`scripts/q08b_renda_prazo.py`) sobre o resultado da Q8 (`resultados/q08_estados_populacao.csv`):

- Renda: rendimento médio mensal real domiciliar per capita de 2017, por UF (IBGE, PNAD Contínua anual, SIDRA tabela 7531), gravado em `dados/externos/populacao_uf_2017.csv`.
- Modelo: ln(compradores por 100 mil hab.) = a + b · ln(renda per capita) + c · prazo real mediano (dias), ajustado por mínimos quadrados nos 27 estados.
- Cenário "prazo de 7 dias": aplica o modelo a cada estado mantendo a renda e trocando o prazo pelo de SP. É uma extrapolação de uma comparação entre estados, não um efeito causal medido.
