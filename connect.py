import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import plotly.express as px

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


def visao_geral_page():
    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")
    st.sidebar.header("Filtros")

    #Filtro: Empresa
    empresa = st.sidebar.multiselect(
        "Empresa",
        options=df["Empresa"].unique(),
        default=df["Empresa"].unique())

    #Filtro: porte de Prestadora
    porte = st.sidebar.multiselect(
        "Porte da Prestadora",
        options=df["Porte da Prestadora"].unique(),
        default=df["Porte da Prestadora"].unique())

    #Filtro: Tecnologia
    tecnologia = st.sidebar.multiselect(
        "Tecnologia",
        options=df["Tecnologia"].unique(),
        default=df["Tecnologia"].unique())

    #Filtro: Tecnologia Geração
    tecnologia_geracao = st.sidebar.multiselect(
        "Tecnologia Geração",
        options=df["Tecnologia Geração"].unique(),
        default=df["Tecnologia Geração"].unique())

    #Filtro Tipo de Pessoa
    tipo_pessoa = st.sidebar.multiselect(
        "Tipo de Pessoa",
        options=df["Tipo de Pessoa"].unique(),
        default=df["Tipo de Pessoa"].unique())

    #Filtro Grupo Econômico
    grupo_economico = st.sidebar.multiselect(
        "Grupo Econômico",
        options=df["Grupo Econômico"].unique(),
        default=df["Grupo Econômico"].unique())

    #Filtro UF
    uf = st.sidebar.multiselect(
        "UF",
        options=df["UF"].unique(),
        default=df["UF"].unique())

paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈")
]

def gerar_graficos_analise(df):
    # 1. Preparar os dados
    # Agrupa por período e empresa
    df_grouped = df.groupby(['periodo', 'Empresa'])['acessos'].sum().unstack(fill_value=0)
    
    # --- GRÁFICO 1: Crescimento do Mercado (Série Temporal) ---
    mercado_total = df_grouped.sum(axis=1).reset_index(name='Total Acessos')
    fig1 = px.line(mercado_total, x='periodo', y='Total Acessos', 
                   title="Evolução do Mercado de Acessos Móveis",
                   markers=True)
    
    # --- GRÁFICO 2: Maior Crescimento Absoluto (Top 10) ---
    crescimento_abs = (df_grouped.iloc[-1] - df_grouped.iloc[-2]).nlargest(10).reset_index()
    crescimento_abs.columns = ['Empresa', 'Crescimento Absoluto']
    fig2 = px.bar(crescimento_abs, x='Crescimento Absoluto', y='Empresa', orientation='h',
                  title="Top 10: Maior Crescimento Absoluto (Último Mês)",
                  color='Crescimento Absoluto')
    
    # --- GRÁFICO 3: Maior Crescimento Percentual (Top 10 com filtro) ---
    crescimento_pct = (df_grouped.pct_change().iloc[-1] * 100).fillna(0)
    # Filtro: considerar apenas empresas com volume relevante para evitar distorções
    filtro = df_grouped.iloc[-1] > 1000 
    top_pct = crescimento_pct[filtro].nlargest(10).reset_index()
    top_pct.columns = ['Empresa', 'Crescimento %']
    
    fig3 = px.bar(top_pct, x='Crescimento %', y='Empresa', orientation='h',
                  title="Top 10: Maior Crescimento Percentual (Volume > 1000)",
                  color='Crescimento %')

    return fig1, fig2, fig3

navegacao = st.navigation(paginas)
navegacao.run()