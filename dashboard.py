'''
T_TT002A_2020S2
216968, Giovanni Bassetto
199617, João Gabriel 
156471, Luiz Felipe Rosa da Silveira
Projeto Final - Dashboard dos dados eleitorais brasileiros do ano de 2020
-

A massa de dados pode ser encontrada em:
https://www.kaggle.com/docstein/brics-world-bank-indicators
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
import dask.dataframe as dd
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math
import os
import time

def convert_to_month(df=None, date_column="date"):
    """Usa uma coluna de datas para criar uma nova coluna que contém
    o número do mes
    """
    # Converte a data de string para datetime
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    # A partir da data obtem o número da semana
    df["month"] = df["date"].dt.month
    # Retorna os dados atualizados
    return df

def add_columns(df=None, nome='', series_code=''):
    """Adiciona colunas ao dataframe, método criado pelo fato do dataset
    em questão trazer os indicadores em linhas, não em colunas
    """      
    #carrega o dataframe do csv que contem os dados desejados
    csv_path_1 = 'data/' + nome
    csv_path_1 = os.path.join(os.path.dirname(__file__), csv_path_1)
    df_query = dd.read_csv(csv_path_1, sep=';')
    df_query = df_query.compute()
    df_query = df_query.sort_values(['CountryName', 'Year'])
    df_query = df_query.loc[(df_query['SeriesCode']== series_code) &
                            (df_query['Year']== 2017)] #somente na ocasião estática
    
    df_query.rename(columns = {'Value': series_code}, inplace = True)
    df_query.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    new_column = df_query[series_code]
    df = df.join(new_column)
    return df

#def clean_database(df=None, linhas=[]):

# CSS para página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# inicialização do objeto Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Gráfico 1 ----------------------------------------------

# csv_path_1 = dados economicos
csv_path_1 = 'data/Economy_Data.csv'
csv_path_1 = os.path.join(os.path.dirname(__file__), csv_path_1)

# atribuição do dataframe
df_graph1_not_treated = dd.read_csv(csv_path_1, sep=';')
df_graph1_not_treated = df_graph1_not_treated.compute()
df_graph1_not_treated = df_graph1_not_treated.sort_values(['CountryName', 'Year'])
rows_to_be_used = ( #Economy_Data (gdp per capita)
                    'NY.GDP.PCAP.CD',
                    #HealthAndPoverty_Data (populacao total, expectativa de vida)
                    'SP.POP.TOTL', 'SP.DYN.LE00.IN')

#remocão das linhas que não serão utilizadas para melhorar a performance
df_remove = df_graph1_not_treated.loc[
    (df_graph1_not_treated['SeriesCode'] != 'NY.GDP.PCAP.CD')]

df_graph1 = df_graph1_not_treated.drop(df_remove.index)

# Primeira atribuição estática
df_graph1_2017 = df_graph1[df_graph1['Year']==2017]

# Chamadas das funções necessárias para manipulação dos dados
df_graph1_2017 = df_graph1_2017.rename(columns = {'Value':'NY.GDP.PCAP.CD'}, inplace = False)
df_graph1_2017 = add_columns(df_graph1_2017, 'HealthAndPoverty_Data.csv', 'SP.POP.TOTL')
df_graph1_2017 = add_columns(df_graph1_2017, 'HealthAndPoverty_Data.csv', 'SP.DYN.LE00.IN')

#definindo informações do mouser hover e tamanho das bolhas do gráfico
hover_text = []
bubble_size = []

for index, row in df_graph1_2017.iterrows():
    hover_text.append(('País: {country}<br>'+
                      'Expectativa de vida: {life}<br>'+
                      'GDP per capita: {gpd}<br>'+
                      'População: {pop}<br>'+
                      'Ano: {year}').format(country=row['CountryName'],
                                            life=row['SP.DYN.LE00.IN'], #SP.DYN.LE00.IN
                                            gpd=row['NY.GDP.PCAP.CD'],#NY.GDP.PCAP.CD
                                            pop=row['SP.POP.TOTL'], #SP.POP.TOTL
                                            year=row['Year']))
    bubble_size.append(math.sqrt(row['SP.POP.TOTL'])) #SP.POP.TOTL

df_graph1_2017['text'] = hover_text
df_graph1_2017['size'] = bubble_size
sizeref = 2.*max(df_graph1_2017['size'])/(100**2)

# Dicionario com os dataframes para país
paises = ['Brazil', 'China', 'India', 'Russian Federation', 'South Africa']
dados_paises = {pais:df_graph1_2017.query("CountryName=='%s'" %pais)
                              for pais in paises}

# Figura base do grafico de bolhas
graph1 = go.Figure()

for paises, pais in dados_paises.items():
    graph1.add_trace(go.Scatter(
        x=pais['NY.GDP.PCAP.CD'], y=pais['SP.DYN.LE00.IN'],
        name=paises, text=pais['text'],
        marker_size=pais['size'],
        ))

# Tune marker appearance and layout
graph1.update_traces(mode='markers', marker=dict(sizemode='area',
                                              sizeref=sizeref, line_width=2))

graph1.update_layout(
    title='Expectativa de vida vs. GDP per capita',
    xaxis=dict(
        title='GDP per capita (US$)',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='Expectativa de vida',
        gridcolor='white',
        gridwidth=2,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
)

# Layout do app
app.layout = html.Div(children=[
    html.H2(children='TT002 - Atividade em Grupo (Dashboard)'),
        html.H5('216968, Giovanni Bassetto'),
        html.H5('199617, João Gabriel'),
        html.H5('156471, Luiz Felipe Rosa da Silveira'),

    # Exercicio 1
    html.Div(
        dcc.Graph(
            id='example-graph',
            figure= graph1
        ), style={'width': '80%', 'padding': '0px 20px 20px 20px', 'verticalAlign':"middle"}
    ),
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
