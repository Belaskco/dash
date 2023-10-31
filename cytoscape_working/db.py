#!/usr/bin/env python
# database.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("/.env")
db_host = os.environ.get("DB_HOST")
db_database = os.environ.get("DB_DATABASE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    host=db_host,
    database=db_database,
    user=db_user,
    password=db_password
)

# Função para executar consultas SQL e retornar os resultados
def executar_consulta_sql(consulta_sql, params=None):
    with conn.cursor() as cursor:
        cursor.execute(consulta_sql, params)
        return cursor.fetchall()

# Query para recuperar os dados iniciais
cst_inicial = """
    SELECT carros.marca, carros.pais_sede, COUNT(*) AS total_vendas
    FROM vendas
    INNER JOIN carros ON vendas.id_carro = carros.id_carro
    GROUP BY carros.marca, carros.pais_sede
"""

# Query para recuperar as opções para dropdown Ano das Vendas
cst_opcoes_dropdown_anos = """
    SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
    FROM vendas
    ORDER BY ano ASC
"""

cst_opcoes_dropdown_paises = """
    SELECT DISTINCT pais_sede
    FROM carros
"""