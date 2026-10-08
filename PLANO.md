# Estudo de e-commerce (base pública da Olist): plano de trabalho

## Objetivo

Responder perguntas de negócio de um marketplace brasileiro **escrevendo SQL**, e entregar um painel em Power BI. É o primeiro projeto feito com a divisão "você escreve, o Claude revisa", para que o código e o histórico de commits mostrem o seu trabalho.

## A base

- **Brazilian E-Commerce Public Dataset by Olist**, no Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Cerca de 100 mil pedidos de 2016 a 2018, em 9 arquivos CSV (pedidos, itens, pagamentos, avaliações, clientes, vendedores, produtos, geolocalização e tradução das categorias).
- Confira na página do Kaggle a licença e cite a fonte no README. Os CSV não vão para o GitHub (são grandes); o README explica onde baixar.

## Preparação (uma vez só)

1. Crie uma conta gratuita no Kaggle, baixe o arquivo da base e descompacte os 9 CSV em `dados\brutos`.
2. Instale o DuckDB para Python: abra o Prompt de Comando e rode `py -m pip install duckdb` (ou `python -m pip install duckdb`).
3. Teste: `py rodar_sql.py sql\00_carga.sql`. Deve aparecer a contagem de linhas de cada tabela.
4. Crie o repositório local e faça o primeiro commit (comandos abaixo).

## Como trabalhar

- Cada arquivo em `sql\` tem perguntas em comentários. **Escreva a consulta embaixo de cada pergunta** e rode com `py rodar_sql.py sql\arquivo.sql`.
- Antes de pedir revisão, confira o resultado com o bom senso: os números fazem sentido? A soma bate com o total?
- Para revisão, me mande o arquivo (ou cole a consulta e o resultado). Eu aponto erros, explico o porquê e sugiro como melhorar, **sem reescrever por você**.
- Se travar mais de 20 minutos numa pergunta, peça uma dica, não a resposta.

## Commits

Faça commits pequenos, ao terminar cada bloco de perguntas. Isso cria o histórico que o recrutador vai ver.

```
git init -b main                      (só na primeira vez)
git add .
git commit -m "Exploração inicial das tabelas"
```

Exemplos de mensagens boas: "Faturamento mensal e ticket médio", "Corrige ticket médio: usa pagamentos e não itens", "Coortes de retenção por mês da primeira compra". A publicação no GitHub fica para o fim; os commits locais já contam com a data em que foram feitos.

## Cronograma sugerido (cerca de 5 semanas)

| Semana | Etapa | Arquivo |
|---|---|---|
| 1 | Carga e exploração: o que tem em cada tabela, período, status, nulos, chaves | `00_carga.sql`, `01_exploracao.sql` |
| 2 | Vendas: faturamento, pedidos, ticket médio, categorias, estados | `02_vendas.sql` |
| 3 | Logística e satisfação: prazo, atraso e efeito do atraso na nota | `03_logistica.sql` |
| 4 | Clientes e vendedores: recompra, coortes, RFM, concentração (Pareto) | `04_clientes.sql`, `05_vendedores.sql` |
| 5 | Tabelas para o Power BI, painel e README | `06_modelo_bi.sql` |

## O que o projeto vai comprovar no currículo

SQL com junções, agregações, CTEs e funções de janela (`ROW_NUMBER`, `LAG`, `NTILE`, soma acumulada); KPIs clássicos de negócio (ticket médio, recompra, retenção, atraso, nota); modelagem para Power BI; e um tema fora do gás.
