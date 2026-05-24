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

#Filtro: porte de Prestadora
porte = st.sidebar.multiselect(
    "Porte da Prestadora",
    options=df["Porte da Prestadora"].unique(),
    default=df["Porte da Prestadora"].unique())

def visao_geral_page():
    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")

paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈")
]


navegacao = st.navigation(paginas)
navegacao.run()