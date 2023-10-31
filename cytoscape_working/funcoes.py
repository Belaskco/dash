#!/usr/bin/env python

# Importar as bibliotecas necessárias
import db

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
    valores = db.executar_consulta_sql(consulta)
    valores = [valor[0] for valor in valores if valor[0] is not None]
    valores.sort()
    return [{'label': 'Todos', 'value': 'todos'}] + [{'label': valor, 'value': valor} for valor in valores]