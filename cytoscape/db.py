#!/usr/bin/env python
# db.py

import os
from sqlalchemy import *
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Impporte as varáveis de ambiente de .env.
load_dotenv(".env")
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_host = os.environ.get("DB_HOST")
db_data = os.environ.get("DB_DATA")

# Crie uma instância da engine para se conectar ao banco de dados PostgreSQL
db_url = f'postgresql://{db_user}:{db_pass}@{db_host}/{db_data}'
engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

# Crie a classe base do SQLAlchemy
Base = declarative_base()

# Defina os modelos para as tabelas
class Vendas(Base):
    __tablename__ = 'vendas'

    id_venda = Column(INTEGER, primary_key=True)
    id_carro = Column(INTEGER, ForeignKey('carros.id_carro'))
    id_cliente = Column(INTEGER, ForeignKey('clientes.id_cliente'))
    data_venda = Column(DATE)
    valor_venda = Column(NUMERIC(precision=10, scale=2))

class Carro(Base):
    __tablename__ = 'carros'

    id_carro = Column(INTEGER, primary_key=True)
    marca = Column(VARCHAR(50))
    modelo = Column(VARCHAR(50))
    ano_fabricacao = Column(INTEGER)
    cor = Column(VARCHAR(50))
    valor_unitario = Column(NUMERIC(precision=10, scale=2))
    data_entrada = Column(DATE)
    pais_sede = Column(String)

# Crie as tabelas no banco de dados, caso ainda não existam
Base.metadata.create_all(engine)

cst_inicial = (
    session.query(
    Carro.marca,
    Carro.pais_sede,
    func.count(Vendas.id_venda)
    .label("total_vendas"))
    .join(Vendas, Vendas.id_carro == Carro.id_carro)
    .group_by(Carro.marca, Carro.pais_sede)
)

# Consulta para obter as opções para dropdown Anos
cst_dropdown_anos = (
    session.query(
        extract('year', Vendas.data_venda).label('ano')
    )
    .distinct()
    .order_by('ano')
)

# Consulta para obter as opções para dropdown Países
cst_dropdown_paises = (
    session.query(
        distinct(Carro.pais_sede)
    )
)

session.close()
