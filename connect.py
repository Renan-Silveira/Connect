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

def crescimento(df):
    dfcrescimento = df.groupby(['periodo', 'Empresa'])['acessos'].sum().unstack(fill_value=0)
    

    mercado_total = dfcrescimento.sum(axis=1).reset_index(name='Total Acessos')
    fig1 = px.line(mercado_total, x='periodo', y='Total Acessos', 
                   title="Evolução do Mercado de Acessos Móveis",
                   markers=True)
    
    mes_atual = dfcrescimento.index[-1]
    mes_anterior = dfcrescimento.index[-2]
    
    # Criamos um DataFrame 'long' para o plotly entender as barras agrupadas
    df_comp = dfcrescimento.loc[[mes_anterior, mes_anterior]].copy() # Estrutura base
    df_comp = dfcrescimento.iloc[-2:].T.reset_index()
    df_comp = df_comp.melt(id_vars='Empresa', var_name='Periodo', value_name='Acessos')
    
    # Filtramos para mostrar apenas as 10 empresas com maior variação absoluta
    top_10_empresas = (dfcrescimento.iloc[-1] - dfcrescimento.iloc[-2]).nlargest(10).index
    df_comp = df_comp[df_comp['Empresa'].isin(top_10_empresas)]
    
    fig2 = px.bar(df_comp, 
                  x='Acessos', 
                  y='Empresa', 
                  color='Periodo', 
                  barmode='group', # Isso coloca as barras lado a lado
                  orientation='h',
                  title=f"Comparativo de Acessos: {mes_anterior} vs {mes_atual}",
                  text_auto='.2s') # Mostra o valor formatado nas barras
    
    crescimento_pct = (dfcrescimento.pct_change().iloc[-1] * 100).fillna(0)

    filtro = dfcrescimento.iloc[-1] > 1000 
    top_pct = crescimento_pct[filtro].nlargest(10).reset_index()
    top_pct.columns = ['Empresa', 'Crescimento %']
    
    fig3 = px.bar(top_pct, x='Crescimento %', y='Empresa', orientation='h',
                  title="Top 10: Maior Crescimento Percentual (Volume > 1000)",
                  color='Crescimento %')

    return fig1, fig2, fig3

def aplicar_filtros(df):
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

def teste():
    print("Teste de Navegação") # Função de teste para verificar a navegação entre páginas, imprime uma mensagem no console quando chamada
    aplicar_filtros(df) # Chama a função aplicar_filtros para exibir os filtros na barra lateral, permitindo que o usuário interaja com os dados e refine a visualização de acordo com suas preferências

def visao_geral_page():

    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")
    st.sidebar.header("Filtros")
    aplicar_filtros(df) # Chama a função aplicar_filtros para exibir os filtros na barra lateral, permitindo que o usuário interaja com os dados e refine a visualização de acordo com suas preferências

    fig1, fig2, fig3 = crescimento(df)

    st.title("Dashboard de Mercado - Acessos Móveis")

    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)
paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈"),
    st.Page(teste, title='Teste', icon="🔍")
]


navegacao = st.navigation(paginas)
navegacao.run()