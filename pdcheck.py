import dash
import dask.dataframe as dd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import os

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
    df_query = df_query.loc[(df_query['SeriesCode']==series_code) &
                            (df_query['Year']== 2017)] #somente na ocasião estática
    
    df_query.rename(columns = {'Value': series_code}, inplace = True)
    df_query.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    new_column = df_query[series_code]
    df = df.join(new_column)
    return df

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

print(df_graph1_2017)
