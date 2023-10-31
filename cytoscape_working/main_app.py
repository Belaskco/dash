#!/usr/bin/env python
# main_app.py

# Importar as bibliotecas necessárias
import pandas as pd
from dash import Input, Output
import dash_app 
import db
import funcoes

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
    parametros_where = []
    clausula_condicional = "WHERE TRUE"
    if ano_selecionado != 'todos':
        clausula_condicional += " AND EXTRACT(YEAR FROM vendas.data_venda) = %s"
        parametros_where.append(int(ano_selecionado))
    if pais_selecionado != 'todos':
        clausula_condicional += " AND carros.pais_sede = %s"
        parametros_where.append(pais_selecionado)

    # Consulta SQL para recuperar os nós e as arestas com base no ano selecionado e no país sede selecionado
    consulta = f"""
        SELECT carros.marca, carros.pais_sede, COUNT(*) AS total_vendas
        FROM vendas
        INNER JOIN carros ON vendas.id_carro = carros.id_carro
        {clausula_condicional}
        GROUP BY carros.marca, carros.pais_sede
    """

    # Executa a consulta e recupera os dados atualizados
    dados_atualizados = db.executar_consulta_sql(consulta, parametros_where)

    # Cria uma nova lista de nós e arestas
    elementos_atualizados = []
    for linha in dados_atualizados:
        elementos_atualizados += funcoes.gerar_elemento_grafico(*linha)

    return elementos_atualizados, str(ano_selecionado)

# Callback para atualizar as opções do dropdown de países sede com base no ano selecionado
@dash_app.app.callback(
    Output('dropdown-pais-sede', 'options'),
    Input('dropdown-ano', 'value')
)
def atualizar_opcoes_paises(ano_selecionado):
    if ano_selecionado == 'todos':
        consulta = db.cst_opcoes_dropdown_paises
    else:
        consulta = f"""
            {db.cst_opcoes_dropdown_paises}
            WHERE id_carro IN (
                SELECT id_carro
                FROM vendas
                WHERE EXTRACT(YEAR FROM data_venda) = {ano_selecionado}
            )
        """
    return funcoes.gerar_opcoes_dropdown('pais_sede', consulta)

# Callback para atualizar as opções do dropdown de anos com base no país selecionado
@dash_app.app.callback(
    Output('dropdown-ano', 'options'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_opcoes_anos(pais_selecionado):

    select_1 = """
    SELECT DISTINCT EXTRACT(YEAR FROM data_venda) AS ano
    FROM vendas
    """

    if pais_selecionado == 'todos':
        consulta = select_1 + """
            ORDER BY ano ASC
        """
    else:
        consulta = select_1 + f"""
            INNER JOIN carros ON vendas.id_carro = carros.id_carro
            WHERE carros.pais_sede = '{pais_selecionado}'
            ORDER BY ano ASC
        """
    return funcoes.gerar_opcoes_dropdown('ano', consulta)

# Callback para atualizar a tabela de vendas com base nas opções selecionadas
@dash_app.app.callback(
    Output('tabela-vendas', 'data'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_tabela_vendas(ano_selecionado, pais_selecionado):

    select_2 = """
        SELECT carros.marca AS marca, COUNT(*) AS total_vendas
        FROM vendas
        INNER JOIN carros ON vendas.id_carro = carros.id_carro
        """

    if ano_selecionado == 'todos' and pais_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para todos os anos e países
        consulta = select_2 + """
            GROUP BY carros.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    elif ano_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para todos os anos e o país selecionado
        consulta = select_2 + f"""
            WHERE carros.pais_sede = '{pais_selecionado}'
            GROUP BY carros.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    elif pais_selecionado == 'todos':
        # Consulta SQL para recuperar o total de vendas por marca para o ano selecionado e todos os países
        consulta = select_2 + f"""
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado}
            GROUP BY carros.marca
            ORDER BY total_vendas DESC, marca ASC
        """
    else:
        # Consulta SQL para recuperar o total de vendas por marca para o ano selecionado e o país selecionado
        consulta = select_2 + f"""
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado} AND carros.pais_sede = '{pais_selecionado}'
            GROUP BY carros.marca
            ORDER BY total_vendas DESC, marca ASC
        """

    # Executa a consulta e recupera os dados
    dados_tabela_vendas = db.executar_consulta_sql(consulta)

    df = pd.DataFrame(dados_tabela_vendas, columns=['marca', 'total_vendas'])

    return df.to_dict('records')

# Callback para atualizar o total de vendas por marca com base nas opções selecionadas
@dash_app.app.callback(
    Output('total-geral', 'children'),
    Input('dropdown-ano', 'value'),
    Input('dropdown-pais-sede', 'value')
)
def atualizar_total_geral(ano_selecionado, pais_selecionado):

    select_3 = """
        SELECT COUNT(*) AS total_geral
        FROM vendas
        INNER JOIN carros ON vendas.id_carro = carros.id_carro
"""
    if ano_selecionado == 'todos' and pais_selecionado == 'todos':
        consulta_total_geral = select_3
        
    elif ano_selecionado == 'todos':
        consulta_total_geral = select_3 + f"""
            WHERE carros.pais_sede = '{pais_selecionado}'
        """
    elif pais_selecionado == 'todos':
        consulta_total_geral = select_3 + f"""
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado}
        """
    else:
        consulta_total_geral = select_3 + f"""
            WHERE EXTRACT(YEAR FROM vendas.data_venda) = {ano_selecionado} AND carros.pais_sede = '{pais_selecionado}'
        """

    total_geral = db.executar_consulta_sql(consulta_total_geral)[0][0]
    if total_geral is not None:
        return f" {total_geral}"
    else:
        return ""

# Executa o servidor Dash
if __name__ == '__main__':
    dash_app.app.run_server(port=8055, debug=True)