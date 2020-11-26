'''
T_TT002A_2020S2
216968, Giovanni Bassetto
199617, João Gabriel 
156471, Luiz Felipe Rosa da Silveira
Projeto Final - Dashboard dos dados eleitorais brasileiros do ano de 2020
-

A massa de dados pode ser encontrada em:
https://www.kaggle.com/lgmoneda/brazil-elections-2020
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

# CSS para página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# inicialização do objeto Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Gráfico 1 ----------------------------------------------

# csv_path_1 = prestacao de contas para consulta de receita
colunas_a_utilizar =['ANO_ELEICAO', 'SG_UF', 'CD_MUNICIPIO', 'DS_GRAU_ESCOLARIDADE',
                     'DS_FAIXA_ETARIA', 'QT_ELEITORES_PERFIL', 'CD_FAIXA_ETARIA',
                     'CD_GRAU_ESCOLARIDADE']
csv_path_1 = 'eleitorado/perfil_eleitorado_2020.csv'
csv_path_1 = os.path.join(os.path.dirname(__file__), csv_path_1)
start = time.time()
df_graph1 = dd.read_csv(csv_path_1, usecols=colunas_a_utilizar, sep=';', encoding='latin-1')
df_graph1 = df_graph1.compute()
end = time.time()
print("Read csv with dask: ",(end-start),"sec")

#definindo informações do mouser hover e tamanho das bolhas do gráfico
df_graph1 = df_graph1.sort_values(['SG_UF', 'CD_MUNICIPIO'])

hover_text = []
bubble_size = []

for index, row in df_graph1.iterrows():
    hover_text.append(('Municipio: {CD_MUNICIPIO}<br>'+
                      'Grau de Escolaridade: {DS_GRAU_ESCOLARIDADE}<br>'+
                      'Faixa etaria: {DS_FAIXA_ETARIA}<br>'+
                      'Quantidade de eleitores: {QT_ELEITORES_PERFIL}<br>'+
                      'Ano: {ANO_ELEICAO}').format(CD_MUNICIPIO=row['CD_MUNICIPIO'],
                                            DS_GRAU_ESCOLARIDADE=row['DS_GRAU_ESCOLARIDADE'],
                                            DS_FAIXA_ETARIA=row['DS_FAIXA_ETARIA'],
                                            QT_ELEITORES_PERFIL=row['QT_ELEITORES_PERFIL'],
                                            ANO_ELEICAO=row['ANO_ELEICAO']))
    bubble_size.append(math.sqrt(row['QT_ELEITORES_PERFIL']))

df_graph1['text'] = hover_text
df_graph1['size'] = bubble_size
sizeref = 2.*max(df_graph1['size'])/(100**2)

# Dicionario com os dataframes para cada estado
siglas_estados = ['SP' 'BA' 'MS' 'MG' 'PR' 'MA' 'GO' 'AL' 'MT' 'PB' 'TO' 'PA' 'PE' 'PI'
 'ES' 'CE' 'RJ' 'RS' 'SC' 'RO' 'RN' 'SE' 'RR' 'AC' 'AM' 'AP']
dados_estados = {estado:df_graph1.query("SG_UF=='%s'" %estado)
                              for estado in siglas_estados}

# Figura base do grafico de bolhas
graph1 = go.Figure()

for siglas_estados, estado in dados_estados.items():
    graph1.add_trace(go.Scatter(
        x=estado['CD_FAIXA_ETARIA'], y=estado['CD_GRAU_ESCOLARIDADE'],
        name=siglas_estados, text=estado['text'],
        marker_size=estado['size'],
        ))

# Tune marker appearance and layout
graph1.update_traces(mode='markers', marker=dict(sizemode='area',
                                              sizeref=sizeref, line_width=2))

graph1.update_layout(
    title='Grau de escolaridade x Faixa etaria',
    xaxis=dict(
        title='Faixa etaria ([idade_Inicial][idade_final])',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='Grau de escolaridade',
        gridcolor='white',
        gridwidth=2,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
)

# Layout do app
app.layout = html.Div(children=[
    html.H1(children='199617, João Gabriel - Atividade em Grupo (dashboard)'),

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
