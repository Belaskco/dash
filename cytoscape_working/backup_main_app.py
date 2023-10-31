#!/usr/bin/env python

# Importar as bibliotecas necessárias
import pandas as pd
import psycopg2
from dash import Dash, Input, Output, html, dcc, dash_table
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="cassioandrade",
    user="cassioandrade",
    password="3003"
)

# Função para executar consultas SQL e retornar os resultados
def executar_consulta_sql(consulta_sql, params=None):
    with conn.cursor() as cursor:
        cursor.execute(consulta_sql, params)
        return cursor.fetchall()

# Função para gerar elementos do gráfico de rede para um nó específico
def gerar_elemento_grafico(marca, pais_sede, total_vendas=None):
    elementos = [{'data': {'id': marca, 'label': marca}}]

    if pais_sede is not None:
        elementos.append({'data': {'id': pais_sede, 'label': pais_sede}})
        elementos.append({'data': {'source': pais_sede, 'target': marca}})

    if total_vendas is not None:
        elementos.append({'data': {'id': str(total_vendas), 'label': str(total_vendas), 'tipo': 'total_vendas'}})
        elementos.append({'data': {'source': marca, 'target': str(total_vendas)}})

    return elementos

# Função para gerar as opções do dropdown com base em uma coluna específica da consulta SQL
def gerar_opcoes_dropdown(coluna, consulta):
    valores = executar_consulta_sql(consulta)
    valores = [valor[0] for valor in valores if valor[0] is not None]
    valores.sort()
    return [{'label': 'Todos', 'value': 'todos'}] + [{'label': valor, 'value': valor} for valor in valores]

# Cria o aplicativo Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)

# Define o estilo CSS com bordas arredondadas
estilo_bordas_arredondadas = {
    'borderRadius': '10px',
}

# Consulta SQL para recuperar os dados iniciais
consulta_inicial = """
    SELECT c.marca, c.pais_sede, COUNT(*) AS total_vendas
    FROM vendas v
    INNER JOIN carros c ON v.id_carro = c.id_carro
    GROUP BY c.marca, c.pais_sede
"""

# Função para gerar as opções do dropdown de anos
consulta_opcoes_dropdown_anos = """
    SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
    FROM vendas
    ORDER BY ano ASC
"""
consulta_opcoes_dropdown_paises = """
    SELECT DISTINCT pais_sede
    FROM carros
"""

# Executa a consulta e recupera os dados iniciais
dados = executar_consulta_sql(consulta_inicial)

# Cria as opções para o dropdown de países sede
opcoes_dropdown_paises = gerar_opcoes_dropdown('pais_sede', consulta_inicial)

# Cria uma lista de nós e arestas para o gráfico de rede com os dados iniciais
elementos_grafico_todos_anos = []
for linha in dados:
    elementos_grafico_todos_anos += gerar_elemento_grafico(*linha)

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
            options=gerar_opcoes_dropdown('ano', consulta_opcoes_dropdown_anos),
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


# Callback para atualizar a quantidade de países disponíveis
@app.callback(
    Output('quantidade-paises', 'children'),
    Input('dropdown-pais-sede', 'options')
)
def atualizar_quantidade_paises(opcoes_paises):
    quantidade_paises = len(opcoes_paises) - 1  # Descontar 1 para excluir a opção "Todos"
    return quantidade_paises

# Callback para atualizar a quantidade de anos disponíveis
@app.callback(
    Output('quantidade-anos', 'children'),
    Input('dropdown-ano', 'options')
)
def atualizar_quantidade_anos(opcoes_anos):
    quantidade_anos = len(opcoes_anos) - 1  # Descontar 1 para excluir a opção "Todos"
    return quantidade_anos

# Callback para atualizar os elementos do gráfico de rede, a tabela de vendas e a marca selecionada
# com base na opção selecionada no dropdown de ano e no dropdown de país sede
@app.callback(
    Output('graph-rede', 'elements'),
    Output('marca-selecionada', 'children'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_elementos_grafico(ano_selecionado, pais_selecionado):
    # Monta a cláusula WHERE para a consulta SQL
    parametros_where = {}
    clausula_condicional = "WHERE 1 = 1"
    if ano_selecionado != 'todos':
        clausula_condicional += " AND EXTRACT(YEAR FROM v.data_venda) = %(ano_selecionado)s"
        parametros_where['ano_selecionado'] = int(ano_selecionado)
    if pais_selecionado != 'todos':
        clausula_condicional += " AND c.pais_sede = %(pais_selecionado)s"
        parametros_where['pais_selecionado'] = pais_selecionado

    # Consulta SQL para recuperar os nós e as arestas com base no ano selecionado e no país sede selecionado
    consulta = f"""
        SELECT c.marca, c.pais_sede, COUNT(*) AS total_vendas
        FROM vendas v
        INNER JOIN carros c ON v.id_carro = c.id_carro
        {clausula_condicional}
        GROUP BY c.marca, c.pais_sede
    """

    # Executa a consulta e recupera os dados atualizados
    dados_atualizados = executar_consulta_sql(consulta, parametros_where)

    # Cria uma nova lista de nós e arestas
    elementos_atualizados = []
    for linha in dados_atualizados:
        elementos_atualizados += gerar_elemento_grafico(*linha)

    return elementos_atualizados, str(ano_selecionado)

# Callback para atualizar as opções do dropdown de países sede com base no ano selecionado
@app.callback(
    Output('dropdown-pais-sede', 'options'),
    Input('dropdown-ano', 'value')
)
def atualizar_opcoes_paises(ano_selecionado):
    if ano_selecionado == 'todos':
        consulta = consulta_opcoes_dropdown_paises
    else:
        consulta = f"""
            {consulta_opcoes_dropdown_paises}
            WHERE id_carro IN (
                SELECT id_carro
                FROM vendas
                WHERE EXTRACT(YEAR FROM data_venda) = {ano_selecionado}
            )
        """
    return gerar_opcoes_dropdown('pais_sede', consulta)

# Callback para atualizar as opções do dropdown de anos com base no país selecionado
@app.callback(
    Output('dropdown-ano', 'options'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_opcoes_anos(pais_selecionado):
    if pais_selecionado == 'todos':
        consulta = """
            SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
            FROM vendas
            ORDER BY ano ASC
        """
    else:
        consulta = f"""
            SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
            FROM vendas v
            INNER JOIN carros c ON v.id_carro = c.id_carro
            WHERE c.pais_sede = '{pais_selecionado}'
            ORDER BY ano ASC
        """
    return gerar_opcoes_dropdown('ano', consulta)

# Callback para atualizar a tabela de vendas com base nas opções selecionadas
@app.callback(
    Output('tabela-vendas', 'data'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_tabela_vendas(ano_selecionado, pais_selecionado):
    if ano_selecionado == 'todos' and pais_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para todos os anos e países
        consulta = """
            SELECT c.marca AS marca, COUNT(*) AS total_vendas
            FROM vendas v
            INNER JOIN carros c ON v.id_carro = c.id_carro
            GROUP BY c.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    elif ano_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para todos os anos e o país selecionado
        consulta = f"""
            SELECT c.marca AS marca, COUNT(*) AS total_vendas
            FROM vendas v
            INNER JOIN carros c ON v.id_carro = c.id_carro
            WHERE c.pais_sede = '{pais_selecionado}'
            GROUP BY c.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    elif pais_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para o ano selecionado e todos os países
        consulta = f"""
            SELECT c.marca AS marca, COUNT(*) AS total_vendas
            FROM vendas v
            INNER JOIN carros c ON v.id_carro = c.id_carro
            WHERE EXTRACT(YEAR FROM v.data_venda) = {ano_selecionado}
            GROUP BY c.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    else:
        # Consulta SQL para recuperar o total de vendas por marca para o ano selecionado e o país selecionado
        consulta = f"""
            SELECT c.marca AS marca, COUNT(*) AS total_vendas
            FROM vendas v
            INNER JOIN carros c ON v.id_carro = c.id_carro
            WHERE EXTRACT(YEAR FROM v.data_venda) = {ano_selecionado} AND c.pais_sede = '{pais_selecionado}'
            GROUP BY c.marca
            ORDER BY total_vendas DESC, marca ASC
        """

    # Executa a consulta e recupera os dados
    dados_tabela_vendas = executar_consulta_sql(consulta)

    df = pd.DataFrame(dados_tabela_vendas, columns=['marca', 'total_vendas'])

    return df.to_dict('records')

# Callback para atualizar o total de vendas por marca com base nas opções selecionadas
@app.callback(
    Output('total-geral', 'children'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_total_geral(ano_selecionado, pais_selecionado):
    if ano_selecionado == 'todos' and pais_selecionado == 'todos':
        consulta_total_geral = """
            SELECT COUNT(*) AS total_geral
            FROM vendas
        """
    elif ano_selecionado == 'todos':
        consulta_total_geral = f"""
            SELECT COUNT(*) AS total_geral
            FROM vendas
            INNER JOIN carros ON vendas.id_carro = carros.id_carro
            WHERE carros.pais_sede = '{pais_selecionado}'
        """
    elif pais_selecionado == 'todos':
        consulta_total_geral = f"""
            SELECT COUNT(*) AS total_geral
            FROM vendas
            INNER JOIN carros ON vendas.id_carro = carros.id_carro
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado}
        """
    else:
        consulta_total_geral = f"""
            SELECT COUNT(*) AS total_geral
            FROM vendas
            INNER JOIN carros ON vendas.id_carro = carros.id_carro
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado} AND carros.pais_sede = '{pais_selecionado}'
        """

    total_geral = executar_consulta_sql(consulta_total_geral)[0][0]
    if total_geral is not None:
        return f" {total_geral}"
    else:
        return ""

# Executa o servidor Dash
if __name__ == '__main__':
    app.run_server(port=8055, debug=True)