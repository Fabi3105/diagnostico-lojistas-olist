-- Carga das tabelas a partir dos CSV em dados/brutos (este arquivo já vem pronto).
-- Rode uma vez: py rodar_sql.py sql\00_carga.sql
-- Se o nome de algum arquivo for diferente no seu download, ajuste aqui.

CREATE OR REPLACE TABLE pedidos     AS SELECT * FROM read_csv_auto('dados/brutos/olist_orders_dataset.csv');
CREATE OR REPLACE TABLE itens       AS SELECT * FROM read_csv_auto('dados/brutos/olist_order_items_dataset.csv');
CREATE OR REPLACE TABLE pagamentos  AS SELECT * FROM read_csv_auto('dados/brutos/olist_order_payments_dataset.csv');
CREATE OR REPLACE TABLE avaliacoes  AS SELECT * FROM read_csv_auto('dados/brutos/olist_order_reviews_dataset.csv');
CREATE OR REPLACE TABLE clientes    AS SELECT * FROM read_csv_auto('dados/brutos/olist_customers_dataset.csv');
CREATE OR REPLACE TABLE vendedores  AS SELECT * FROM read_csv_auto('dados/brutos/olist_sellers_dataset.csv');
CREATE OR REPLACE TABLE produtos    AS SELECT * FROM read_csv_auto('dados/brutos/olist_products_dataset.csv');
CREATE OR REPLACE TABLE geolocalizacao AS SELECT * FROM read_csv_auto('dados/brutos/olist_geolocation_dataset.csv');
CREATE OR REPLACE TABLE categorias  AS SELECT * FROM read_csv_auto('dados/brutos/product_category_name_translation.csv');

-- Conferência: linhas por tabela
SELECT 'pedidos' AS tabela, COUNT(*) AS linhas FROM pedidos
UNION ALL SELECT 'itens', COUNT(*) FROM itens
UNION ALL SELECT 'pagamentos', COUNT(*) FROM pagamentos
UNION ALL SELECT 'avaliacoes', COUNT(*) FROM avaliacoes
UNION ALL SELECT 'clientes', COUNT(*) FROM clientes
UNION ALL SELECT 'vendedores', COUNT(*) FROM vendedores
UNION ALL SELECT 'produtos', COUNT(*) FROM produtos
UNION ALL SELECT 'geolocalizacao', COUNT(*) FROM geolocalizacao
UNION ALL SELECT 'categorias', COUNT(*) FROM categorias;

-- Colunas e tipos de cada tabela
SELECT table_name AS tabela, column_name AS coluna, data_type AS tipo
FROM information_schema.columns
WHERE table_schema = 'main'
ORDER BY table_name, ordinal_position;
