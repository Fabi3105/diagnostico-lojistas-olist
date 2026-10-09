# Lojistas da Olist nos marketplaces: diagnóstico e direcionamento

Estudo independente com a base pública da Olist (Kaggle, 2016-2018), feito como projeto de portfólio em análise de dados.
A pergunta central: **o que faz um lojista continuar vendendo pela Olist, e o que a Olist pode fazer a respeito?**

- **[RELATORIO.pdf](RELATORIO.pdf)** (ou [RELATORIO.md](RELATORIO.md)): sumário executivo, achados, soluções ordenadas por custo, indicadores e método. 16 páginas.
- **[Painel interativo](https://fabi3105.github.io/diagnostico-lojistas-olist/)** (`index.html`): filtros de período, região, estado e categoria. Também abre direto do arquivo, sem servidor.
- **[DIARIO_DECISOES.md](DIARIO_DECISOES.md)**: cada pergunta, a decisão de método, o resultado e a revisão, na ordem em que aconteceram.
- **[BRIEFING_NEGOCIO.md](BRIEFING_NEGOCIO.md)**: como a Olist ganha dinheiro e quem é o cliente dela, levantado antes da análise.

## Autoria e método

Fabian Aliatti Mayer definiu as perguntas, tomou as decisões de método, revisou e aprovou cada resultado e formulou as soluções.
A execução técnica (consultas, programas, classificação dos comentários e redação para revisão) teve apoio de inteligência artificial (Claude).
A seção "Método" do relatório descreve essa divisão e as validações feitas.

## Estrutura

| Pasta ou arquivo | Conteúdo |
|---|---|
| `sql/` | Carga da base e as consultas das perguntas Q1 a Q10 (dialeto DuckDB; `scripts/rodar_sql.py` as executa também em SQLite) |
| `scripts/` | Programas em Python: validação da base, análises A a I, indicadores padrão, gráficos, painel e conferência do relatório |
| `metodo/` | Método das etapas que não são só SQL (Q8b, C) e as instruções dadas aos agentes de IA na classificação dos comentários |
| `resultados/` | Saída de cada análise em CSV (separador `;`, decimal `,`) e os gráficos em `resultados/graficos/` |
| `dados/externos/` | População e renda por estado (IBGE) |
| `dados/brutos/` | Os CSVs da base, **não versionados**: baixe do Kaggle (ver abaixo) |

## Como reproduzir

1. Baixe o *Brazilian E-Commerce Public Dataset by Olist* no Kaggle e descompacte os CSVs em `dados/brutos/`.
2. Instale os pacotes: `pip install -r requirements.txt` (Python 3.10 ou superior).
3. Rode tudo na ordem: `cd scripts` e `python rodar_tudo.py`. A primeira execução cria a cópia SQLite da base em `dados/olist.sqlite`.
   Se a pasta estiver em disco sincronizado ou em rede e o SQLite falhar com *disk I/O error*, defina a variável de ambiente `OLIST_SQLITE` com um caminho local.
4. Ao final, `resultados/conferencia_relatorio.csv` mostra se os números do relatório batem com os CSVs.

A classificação dos 8.706 comentários de nota 1 foi feita por agentes de IA e validada por duas classificações independentes e por uma amostra classificada manualmente (kappa no relatório). Os rótulos publicados (`resultados/qC_rotulos_por_pedido.csv`) são a entrada dos scripts; os textos dos comentários não são republicados.

## Fontes e licença

Base: *Brazilian E-Commerce Public Dataset by Olist* (Kaggle), licença CC BY-NC-SA 4.0. População e renda: IBGE, SIDRA tabelas 6579 e 7531.
Este estudo é independente e não tem vínculo com a Olist. Os resultados valem para a amostra pública e não devem ser lidos como números da empresa.
