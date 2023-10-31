#!/usr/bin/env python
# dash_app.py

# Importar as bibliotecas necessárias
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table
from db import *
from funcoes import gerar_elemento_grafico, gerar_opcoes_dropdown

# Cria o aplicativo Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)

# Define o estilo CSS com bordas arredondadas
estilo_bordas_arredondadas = {
    'borderRadius': '10px',
}

# Consulta SQL para recuperar os dados iniciais
dados_iniciais = session.query(Carro.marca, Carro.pais_sede, Vendas.valor_venda).join(Vendas).all()

# Cria as opções para o dropdown de países sede
opcoes_dropdown_paises = session.query(Carro.pais_sede.distinct()).all()
opcoes_dropdown_paises = [{'label': pais[0], 'value': pais[0]} for pais in opcoes_dropdown_paises]

# Cria uma lista de nós e arestas para o gráfico de rede com os dados iniciais
elementos_grafico_todos_anos = []
for linha in dados_iniciais:
    elementos_grafico_todos_anos += gerar_elemento_grafico(linha[0], linha[1], linha[2])

# Layout do aplicativo
app.layout = dbc.Container(children=[
    html.H1(children=[
        "Dashboard de Vendas: ",
        html.Span(id='marca-selecionada')
    ]),
    
    # Dropdown para seleção do país sede
    html.Div([
        html.Label("País Sede: "),
        html.Span(id='quantidade-paises', style={'margin-left': '10px'}),
        dcc.Dropdown(
            id='dropdown-pais-sede',
            options=opcoes_dropdown_paises,
            value='todos',
            clearable=False,
            className='form-control',
            style=estilo_bordas_arredondadas
        )
    ], style={'display': 'inline-block', 'width': '25%'}),

    # Separador
    html.Span('|', style={'display': 'inline-block', 'margin': '0px 5px'}),
    
    # Dropdown para seleção do ano das vendas
    html.Div([
        html.Label("Ano das Vendas:"),
        html.Span(id='quantidade-anos', style={'margin-left': '10px'}),
        dcc.Dropdown(
            id='dropdown-ano',
            options=gerar_opcoes_dropdown('ano', cst_dropdown_anos),
            value='todos',
            clearable=False,
            className='form-control',
            style=estilo_bordas_arredondadas
        )
    ], style={'width': '25%', 'display': 'inline-block'}),
    
    html.Hr(),
    
    # Dois elementos lado a lado: Gráfico de Rede e Tabela de Vendas
    dbc.Row([
        # Coluna do Gráfico de Rede
        dbc.Col([
            html.Label("Gráfico de Rede:"),
            html.Div(
                cyto.Cytoscape(
                    id='graph-rede',
                    layout={'name': 'breadthfirst'},
                    style={'width': '100%', 'height': '70vh'},
                    elements=elementos_grafico_todos_anos,
                    stylesheet=[
                    # Estilo dos nós
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'background-color': '#48A5DB'
                        }
                    },
                    # Estilo do nó "total_vendas" com alinhamento ao centro
                    {
                        'selector': 'node[tipo="total_vendas"]',
                        'style': {
                            'label': 'data(label)',
                            'background-color': '#48A5DB',
                            'text-valign': 'center',
                            'text-halign': 'center'
                        }
                    },
                    # Estilo das arestas
                    {
                        'selector': 'edge',
                        'style': {
                            'label': 'data(label)',
                            'line-color': '#7BD8FE'
                        }
                    }
                ]
            ),
                style={'border': '1px solid gray', 'borderRadius': '10px', 'padding': '10px', 'color':'white'}
            )
        ], width=9),
        
        # Coluna da Tabela de Vendas
        dbc.Col([
            html.Label("Total de Vendas por Marca: "),
            html.Span(id='total-geral'),
            html.Div(
                dash_table.DataTable(
                    id='tabela-vendas',
                    sort_action='native',
                    columns=[{"name": "Marca", "id": "marca"}, {"name": "Total de Vendas", "id": "total_vendas"}],
                    style_table={'height': '70vh', 'overflowY': 'auto', 'borderCollapse': 'separate', 'borderSpacing': '0px'},
                    style_header={'backgroundColor': '#48A5DB', 'fontWeight': 'bold'},
                    style_cell={'padding': '8px', 'border': '1px solid gray', 'borderRadius': '10px', 'fontSize': '10px'}
                ),
                style={'border': '1px solid gray', 'borderRadius': '10px', 'padding': '10px', 'color':'black'}
            )
        ], width=3)
    ])
])
