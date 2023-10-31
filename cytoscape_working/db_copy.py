#!/usr/bin/env python
# database.py

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

load_dotenv("/.env")
db_host = os.environ.get("DB_HOST")
db_database = os.environ.get("DB_DATABASE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

# Crie uma instância da engine para se conectar ao banco de dados PostgreSQL
db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_database}'
engine = create_engine(db_url)

# Crie a classe base do SQLAlchemy
Base = declarative_base()

# Defina os modelos para as tabelas 'vendas' e 'carros'
class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True)
    id_carro = Column(Integer, ForeignKey('carros.id_carro'))
    data_venda = Column(String)
    # Adicione outras colunas conforme necessário

class Carro(Base):
    __tablename__ = 'carros'

    id_carro = Column(Integer, primary_key=True)
    marca = Column(String)
    pais_sede = Column(String)
    # Adicione outras colunas conforme necessário
    vendas = relationship("Venda", backref="carro")  # Relacionamento um para muitos

# Crie as tabelas no banco de dados, caso ainda não existam
Base.metadata.create_all(engine)

# Função para executar consultas SQL utilizando o SQLAlchemy
def executar_consulta_sql(consulta, params=None):
    with engine.connect() as connection:
        result = connection.execute(consulta, params)
        return result.fetchall()

# Exemplo de como utilizar a função para obter os dados iniciais
cst_inicial = """
    SELECT carros.marca, carros.pais_sede, COUNT(*) AS total_vendas
    FROM vendas
    INNER JOIN carros ON vendas.id_carro = carros.id_carro
    GROUP BY carros.marca, carros.pais_sede
"""

resultado_inicial = executar_consulta_sql(cst_inicial)
for marca, pais_sede, total_vendas in resultado_inicial:
    print(marca, pais_sede, total_vendas)

# Exemplo de como utilizar a função para obter as opções para dropdown Ano das Vendas
cst_opcoes_dropdown_anos = """
    SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
    FROM vendas
    ORDER BY ano ASC
"""

resultado_dropdown_anos = executar_consulta_sql(cst_opcoes_dropdown_anos)
for row in resultado_dropdown_anos:
    print(row[0])

# Exemplo de como utilizar a função para obter as opções para dropdown Países
cst_opcoes_dropdown_paises = """
    SELECT DISTINCT pais_sede
    FROM carros
"""

resultado_dropdown_paises = executar_consulta_sql(cst_opcoes_dropdown_paises)
for row in resultado_dropdown_paises:
    print(row[0])
