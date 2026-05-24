import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env


DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED") # Diretório onde o arquivo pré-processado será salvo, definido como uma string para facilitar a referência em todo o código
df = pd.read_parquet(os.path.join(DIR_DATAPROCESSED, "preprocessado.parquet")) # Lê o arquivo Parquet pré-processado usando o Pandas e armazena em um DataFrame para análise e visualização
df = pd.DataFrame(df) # Converte o DataFrame para garantir que seja do tipo Pandas, caso a leitura do Parquet retorne um tipo diferente (como um DataFrame do Polars ou PyArrow) e para facilitar a manipulação dos dados usando as funcionalidades do Pandas.  


st.set_page_config(
    page_title="Intel de Mercado - Connect/Virtueyes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.sidebar.header("Filtros")

#Filtro: Empresa
empresa = st.sidebar.multiselect(
    "Empresa",
    options=df["Empresa"].unique())

#Filtro: porte de Prestadora
porte = st.sidebar.multiselect(
    "Porte da Prestadora",
    options=df["Porte da Prestadora"].unique())

#Filtro: Tecnologia
tecnologia = st.sidebar.multiselect(
    "Tecnologia",
    options=df["Tecnologia"].unique())

#Filtro: Tecnologia Geração
tecnologia_geracao = st.sidebar.multiselect(
    "Tecnologia Geração",
    options=df["Tecnologia Geração"].unique())

#Filtro Tipo de Pessoa
tipo_pessoa = st.sidebar.multiselect(
    "Tipo de Pessoa",
    options=df["Tipo de Pessoa"].unique())

#Filtro Grupo Econômico
grupo_economico = st.sidebar.multiselect(
    "Grupo Econômico",
    options=df["Grupo Econômico"].unique())

#Filtro UF
uf = st.sidebar.multiselect(
    "UF",
    options=df["UF"].unique(),
    default=df["UF"].unique())

def visao_geral_page():
    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")

paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈")
]


navegacao = st.navigation(paginas)
navegacao.run()