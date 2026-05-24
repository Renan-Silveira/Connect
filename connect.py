import streamlit as st
import pandas as pd
import numpy as np



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

paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈")
]


navegacao = st.navigation(paginas)
navegacao.run()