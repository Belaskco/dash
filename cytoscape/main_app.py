#!/usr/bin/env python
# main_app.py

# Importar as bibliotecas necessárias
import funcoes
import dash_app
import pandas as pd
from db import *
from dash import Input, Output

# Callback para atualizar a quantidade de países disponíveis
@dash_app.app.callback(
    Output('quantidade-paises', 'children'),
    Input('dropdown-pais-sede', 'options')
)
def atualizar_quantidade_paises(opcoes_paises):
    quantidade_paises = len(opcoes_paises) - 1  # Descontar 1 para excluir a opção "Todos"
    return quantidade_paises

# Callback para atualizar a quantidade de anos disponíveis
@dash_app.app.callback(
    Output('quantidade-anos', 'children'),
    Input('dropdown-ano', 'options')
)
def atualizar_quantidade_anos(opcoes_anos):
    quantidade_anos = len(opcoes_anos) - 1  # Descontar 1 para excluir a opção "Todos"
    return quantidade_anos

# Callback para atualizar os elementos do gráfico de rede, a tabela de vendas e a marca selecionada
# com base na opção selecionada no dropdown de ano e no dropdown de país sede
@dash_app.app.callback(
    Output('graph-rede', 'elements'),
    Output('marca-selecionada', 'children'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_elementos_graficos(ano_selecionado, pais_selecionado):
    # Monta a cláusula WHERE para a consulta SQL
    filtros = []
    if ano_selecionado and ano_selecionado != 'todos':
        filtros.append(extract('year', Vendas.data_venda) == int(ano_selecionado))
    if pais_selecionado and pais_selecionado != 'todos':
        filtros.append(Carro.pais_sede == pais_selecionado)

    # Consulta SQL para recuperar os nós e as arestas com base no ano selecionado e no país sede selecionado
    consulta = (
        session.query(
        Carro.marca,
        Carro.pais_sede,
        func.count(Vendas.id_venda)
        .label('total_vendas'))
        .join(Vendas, Vendas.id_carro == Carro.id_carro)
        .filter(*filtros)
        .group_by(Carro.marca, Carro.pais_sede)
    )

    # Executa a consulta e recupera os dados atualizados
    dados_atualizados = consulta.all()

    # Cria uma nova lista de nós e arestas
    elementos_atualizados = []
    for marca, pais, total_vendas in dados_atualizados:
        elementos_atualizados += funcoes.gerar_elemento_grafico(marca, pais, total_vendas)

    return elementos_atualizados, str(ano_selecionado)

# Callback para atualizar as opções do dropdown de países sede com base no ano selecionado
@dash_app.app.callback(
    Output('dropdown-pais-sede', 'options'),
    Input('dropdown-ano', 'value')
)
def atualizar_opcoes_paises(ano_selecionado):
    if ano_selecionado == 'todos':
        consulta = session.query(Carro.pais_sede).distinct()
    else:
        consulta = (
            session.query(Carro.pais_sede)
            .filter(Carro.id_carro.in_(
                session.query(Vendas.id_carro)
                .filter(extract('year', Vendas.data_venda) == int(ano_selecionado))
            ))
            .distinct()
        )

    return funcoes.gerar_opcoes_dropdown('pais_sede', consulta)

# Callback para atualizar as opções do dropdown de anos com base no país selecionado
@dash_app.app.callback(
    Output('dropdown-ano', 'options'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_opcoes_anos(pais_selecionado):
    consulta = (
        session.query(extract('year', Vendas.data_venda).label('ano'))
        .join(Carro, Vendas.id_carro == Carro.id_carro)
    )

    if pais_selecionado != 'todos':
        consulta = consulta.filter(Carro.pais_sede == pais_selecionado)

    consulta = consulta.order_by('ano').distinct()

    return funcoes.gerar_opcoes_dropdown('ano', consulta)

# Callback para atualizar a tabela de vendas com base nas opções selecionadas
@dash_app.app.callback(
    Output('tabela-vendas', 'data'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_tabela_vendas(ano_selecionado, pais_selecionado):
    consulta = (
        session.query(Carro.marca.label('marca'), func.count(Vendas.id_venda).label('total_vendas'))
        .join(Vendas, Vendas.id_carro == Carro.id_carro)
    )

    if ano_selecionado and ano_selecionado != 'todos':
        consulta = consulta.filter(extract('year', Vendas.data_venda) == int(ano_selecionado))

    if pais_selecionado and pais_selecionado != 'todos':
        consulta = consulta.filter(Carro.pais_sede == pais_selecionado)

    consulta = consulta.group_by(Carro.marca).order_by(func.count(Vendas.id_venda).desc(), Carro.marca)

    dados_tabela_vendas = consulta.all()

    df = pd.DataFrame(dados_tabela_vendas, columns=['marca', 'total_vendas'])

    return df.to_dict('records')

# Callback para atualizar o total de vendas por marca com base nas opções selecionadas
@dash_app.app.callback(
    Output('total-geral', 'children'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_total_geral(ano_selecionado, pais_selecionado):
    consulta = (
        session.query(
        func.count(Vendas.id_venda)
        .label('total_geral'))
        .join(Vendas, Vendas.id_carro == Carro.id_carro)
    )
    if ano_selecionado and ano_selecionado != 'todos':
        consulta = consulta.filter(extract('year', Vendas.data_venda) == int(ano_selecionado))

    if pais_selecionado and pais_selecionado != 'todos':
        consulta = consulta.filter(Carro.pais_sede == pais_selecionado)

    total_geral = consulta.scalar()

    if total_geral is not None:
        return f" {total_geral}"
    else:
        return ""

# Executa o servidor Dash
if __name__ == '__main__':
    dash_app.app.run_server(port=8055, debug=True)