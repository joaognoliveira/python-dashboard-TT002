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
    # Carrega o dataframe do csv que contem os dados desejados
    csv_path_1 = 'data/' + nome
    csv_path_1 = os.path.join(os.path.dirname(__file__), csv_path_1)
    df_query = dd.read_csv(csv_path_1, sep=';')
    df_query = df_query.compute()
    df_query = df_query.sort_values(['CountryName', 'Year'])
    df_query = df_query.loc[(df_query['SeriesCode']== series_code)]

    # Renomeia a coluna de valores para exibir o seriescode desejado
    df_query.rename(columns = {'Value': series_code}, inplace = True)

    ''' "Reseta" a indexação para evitar valores nulos. "ah mas isso pode acabar
    enviesando a exibição de valores para filtros maiores". "De fato, porém
    acredito que o mesmo tratamento de sort, ou seja, por country name e ano
    bastaria nesse caso'''
    df_query.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Atribui a nova linha de valores filtrados pelo loc a coluna nova
    new_column = df_query[series_code]
    df = df.join(new_column)
    return df

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

# Chamadas das funções necessárias para manipulação dos dados
df_graph1 = df_graph1.rename(columns = {'Value':'NY.GDP.PCAP.CD'}, inplace = False)
df_graph1 = add_columns(df_graph1, 'HealthAndPoverty_Data.csv', 'SP.POP.TOTL')
df_graph1 = add_columns(df_graph1, 'HealthAndPoverty_Data.csv', 'SP.DYN.LE00.IN')

#definindo informações do mouser hover e tamanho das bolhas do gráfico
hover_text = []
bubble_size = []

for index, row in df_graph1.iterrows():
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

df_graph1['text'] = hover_text
df_graph1['size'] = bubble_size
sizeref = 2.*max(df_graph1['size'])/(100**2)

# Layout do app
app.layout = html.Div(children=[
    html.H2(children='TT002 - Atividade em Grupo (Dashboard)'),
        html.H5('216968, Giovanni Bassetto'),
        html.H5('199617, João Gabriel'),
        html.H5('156471, Luiz Felipe Rosa da Silveira'),

    # Bubble_chart
    html.Div(
        dcc.Graph(
            id='bubble_scatter_graph',
            #figure= graph1
        ), style={'width': '80%', 'padding': '0px 20px 20px 20px', 'verticalAlign':"middle"}
    ),

    html.Div(
        dcc.Slider(
            id= 'slider-bubble_chart',
            min=df_graph1['Year'].min(),
            max=df_graph1['Year'].max(),
            value= df_graph1['Year'].min(),
            marks={int(year): '{}'.format(year)[:-2] for year in df_graph1['Year'].unique()},
            step=None   
        ), style={'width': '80%', 'padding': '20px 20px 20px 20px', 'verticalAlign':"middle"}
    ),
])

# callback que atualiza o bubble chart com o valor do ano no slider
@app.callback(
    dash.dependencies.Output('bubble_scatter_graph', 'figure'),
    [dash.dependencies.Input('slider-bubble_chart', 'value')]
)
def update_bubble_chart_slider(value):
    df_by_Year = df_graph1[df_graph1['Year']==value]

    # Figura base do bubble chart
    df_by_Year = go.Figure()
    
    # Dicionario com os dataframes para cada país
    paises = ['Brazil', 'China', 'India', 'Russian Federation', 'South Africa']
    dados_paises = {pais:df_graph1.query("CountryName=='%s' & Year=='%f'" % (pais, value))
                              for pais in paises}

    for paises, pais in dados_paises.items():
        df_by_Year.add_trace(go.Scatter(
            x=pais['NY.GDP.PCAP.CD'], y=pais['SP.DYN.LE00.IN'],
            name=paises, text=pais['text'],
            marker_size=pais['size'],
            ))

    # Aparencia e layout do marcador
    df_by_Year.update_traces(mode='markers', marker=dict(sizemode='area',
                                                sizeref=sizeref, line_width=2))

    df_by_Year.update_layout(
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
        transition_duration= 600,
    )
    return df_by_Year

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
