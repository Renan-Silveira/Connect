import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import plotly.express as px

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env


DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED") # Diretório onde o arquivo pré-processado será salvo, definido como uma string para facilitar a referência em todo o código
df = pd.read_parquet(os.path.join(DIR_DATAPROCESSED, "preprocessado.parquet")) # Lê o arquivo Parquet pré-processado usando o Pandas e armazena em um DataFrame
df = pd.DataFrame(df) # Converte o DataFrame para garantir que seja do tipo Pandas


st.set_page_config(
    page_title="Intel de Mercado - Connect/Virtueyes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    .main { background-color: #000c1f; }
    .stMetric {
        background-color: #001a3d;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #d4ff00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2 { color: #ffffff; font-family: 'Urbanist', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

def crescimento(df):

    dfcrescimento = df.groupby(['periodo', 'Empresa'])['acessos'].sum().unstack(fill_value=0)
    
    atual = dfcrescimento.iloc[-1]
    anterior = dfcrescimento.iloc[-2]
    
    total_atual = atual.sum()
    total_anterior = anterior.sum()
    variacao_total = ((total_atual - total_anterior) / total_anterior) * 100

    empresa_alvo = "Connect Iot Solutions Ltda"
    if empresa_alvo in atual.index:
        val_connect_atual = atual[empresa_alvo]
        val_connect_ant = anterior[empresa_alvo]
        var_connect = ((val_connect_atual - val_connect_ant) / val_connect_ant) * 100
    else:
        val_connect_atual = 0
        var_connect = 0

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(
            label="Total Acessos Mercado", 
            value=f"{total_atual/1e6:.2f}M", 
            delta=f"{variacao_total:.1f}%"
        )
        
    with c2:
        st.metric(
            label="Acessos Connect IoT", 
            value=f"{val_connect_atual:,.0f}", 
            delta=f"{var_connect:.1f}%"
        )
        
    with c3:
        lider_nome = atual.idxmax()
        lider_valor = atual.max()
        st.metric(
            label=f"Líder: {lider_nome}", 
            value=f"{lider_valor/1e6:.2f}M"
        )

    total_atual = dfcrescimento.iloc[-1].sum()
    total_anterior = dfcrescimento.iloc[-2].sum()
    
    crescimento_mom_total = ((total_atual - total_anterior) / total_anterior) * 100
    
    crescimento_medio_empresas = dfcrescimento.pct_change().iloc[-1].mean() * 100
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Acessos (Mês Atual)", 
            value=f"{total_atual/1e6:.2f}M", 
            delta=f"{crescimento_mom_total:.2f}% (MoM Total)"
        )

    with col2:
        st.metric(
            label="Velocidade Média (Empresas)", 
            value=f"{crescimento_medio_empresas:.2f}%", 
            help="Média de crescimento percentual de todas as empresas no período."
        )

    with col3:
        # Contagem de empresas em crescimento positivo
        empresas_crescendo = (dfcrescimento.iloc[-1] > dfcrescimento.iloc[-2]).sum()
        total_empresas = len(dfcrescimento.columns)
        st.metric(
            label="Empresas em Expansão", 
            value=f"{empresas_crescendo} de {total_empresas}",
            delta=f"{ (empresas_crescendo/total_empresas)*100:.0f}% do market cap",
            delta_color="normal"
        )
    # FIGURA 1 - Evolução do Mercado
    mercado_total = dfcrescimento.sum(axis=1).reset_index(name='Total Acessos')
    fig1 = px.line(mercado_total, x='periodo', y='Total Acessos', 
                   title="Evolução do Mercado de Acessos Móveis",
                   markers=True)
    
    ## FIGURA 2 - Comparativo entre os dois últimos meses para as 10 maiores empresas
    mes_atual = dfcrescimento.index[-1]
    mes_anterior = dfcrescimento.index[-2]
    df_comp = dfcrescimento.loc[[mes_anterior, mes_anterior]].copy()
    df_comp = dfcrescimento.iloc[-2:].T.reset_index()
    df_comp = df_comp.melt(id_vars='Empresa', var_name='Periodo', value_name='Acessos')
    top_10_empresas = (dfcrescimento.iloc[-1] - dfcrescimento.iloc[-2]).nlargest(10).index
    df_comp = df_comp[df_comp['Empresa'].isin(top_10_empresas)]
    ordem_empresas = df_comp[df_comp['Periodo'] == mes_atual].sort_values(by='Acessos', ascending=True)['Empresa'].tolist()
    fig2 = px.bar(df_comp, 
                  x='Acessos', 
                  y='Empresa', 
                  color='Periodo', 
                  barmode='group',
                  orientation='h',
                  title=f"Comparativo de Acessos: {mes_anterior} vs {mes_atual}",
                  text_auto='.2s') 
    fig2.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': ordem_empresas})
    
    # FIGURA 3 - Top 10 empresas com maior crescimento percentual (com filtro de volume mínimo para evitar distorções)
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
    
    df_filtrado = df[
        (df["Empresa"].isin(empresa)) &
        (df["Porte da Prestadora"].isin(porte)) &
        (df["Tecnologia"].isin(tecnologia)) &
        (df["Tecnologia Geração"].isin(tecnologia_geracao)) &
        (df["Tipo de Pessoa"].isin(tipo_pessoa)) &
        (df["Grupo Econômico"].isin(grupo_economico)) &
        (df["UF"].isin(uf))
    ]
    return df_filtrado

def teste():
    print("Teste de Navegação") # Função de teste para verificar a navegação entre páginas, imprime uma mensagem no console quando chamada
    aplicar_filtros(df) # Chama a função aplicar_filtros para exibir os filtros na barra lateral, permitindo que o usuário interaja com os dados e refine a visualização de acordo com suas preferências

def visao_geral_page():

    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")
    st.sidebar.header("Filtros")

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