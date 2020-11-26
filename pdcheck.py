import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import os

csv_path = 'eleitorado/perfil_eleitorado_2020.csv'
csv_path = os.path.join(os.path.dirname(__file__), csv_path)

df1 = pd.read_csv(csv_path, sep=';', encoding='latin-1')

print(df1.head(10))
print(df1.columns)
print(len(df1['DS_MUN_SIT_BIOMETRIA'].unique()))
