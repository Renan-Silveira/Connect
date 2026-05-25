import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

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
    mercado_total = (
    dfcrescimento
    .sum(axis=1)
    .reset_index(name='Total Acessos')
    )

    mercado_total['periodo'] = pd.to_datetime(mercado_total['periodo'])
    mercado_total = mercado_total.sort_values('periodo') #Ordenando os dados

    
    mercado_total['Crescimento %'] = (mercado_total['Total Acessos'].pct_change() * 100) # Crescimento percentual

    mercado_total['MM3'] = (mercado_total['Total Acessos'].rolling(3).mean()) # Média móvel de 3 períodos

    
    ultimo_valor = mercado_total.iloc[-1] # Último valor

    
    pico = mercado_total.loc[mercado_total['Total Acessos'].idxmax()] # Pico

    
    minimo = mercado_total.loc[mercado_total['Total Acessos'].idxmin()] # Menor valor

    
    fig1 = go.Figure() # Figura principal

    # Linha principal
    fig1.add_trace(
        go.Scatter(
            x=mercado_total['periodo'],
            y=mercado_total['Total Acessos'],
            mode='lines+markers',
            name='Total Acessos',
            line=dict(width=3),
            hovertemplate=
            '<b>%{x|%m/%Y}</b><br>' +
            'Acessos: %{y:,.0f}<extra></extra>'
        )
    )

    # Média móvel
    fig1.add_trace(
        go.Scatter(
            x=mercado_total['periodo'],
            y=mercado_total['MM3'],
            mode='lines',
            name='Média móvel (3)',
            line=dict(dash='dash')
        )
    )

    # Destaque pico
    fig1.add_trace(
        go.Scatter(
            x=[pico['periodo']],
            y=[pico['Total Acessos']],
            mode='markers+text',
            text=['Pico'],
            textposition='top center',
            marker=dict(size=12),
            name='Pico'
        )
    )

    # Destaque mínimo
    fig1.add_trace(
        go.Scatter(
            x=[minimo['periodo']],
            y=[minimo['Total Acessos']],
            mode='markers+text',
            text=['Mínimo'],
            textposition='bottom center',
            marker=dict(size=12),
            name='Mínimo'
        )
    )

    # Layout
    fig1.update_layout( title='Evolução do Mercado de Acessos Móveis', xaxis_title='Período', yaxis_title='Total de Acessos', hovermode='x unified', template='plotly_white', height=600, legend_title='Indicadores')

    # Anotação último valor
    fig1.add_annotation(x=ultimo_valor['periodo'], y=ultimo_valor['Total Acessos'],
        text=(
            f"Último:<br>"
            f"{ultimo_valor['Total Acessos']:,.0f}<br>"
            f"{ultimo_valor['Crescimento %']:.2f}%"), showarrow=True, arrowhead=2)

    
    fig1.update_yaxes(tickformat=',.0f') # Formatação eixo Y
    
    ## FIGURA 2 - Comparativo entre os dois últimos meses para as 10 maiores empresas
    mes_atual = dfcrescimento.index[-1]
    mes_anterior = dfcrescimento.index[-2]
    df_comp = dfcrescimento.loc[[mes_anterior, mes_anterior]].copy() # Seleciona os dados dos dois últimos meses para comparação, criando um novo DataFrame que contém apenas esses períodos para facilitar a análise comparativa entre eles.
    df_comp = dfcrescimento.iloc[-2:].T.reset_index() # Transpõe os dados para ter as empresas como linhas e os períodos como colunas, facilitando a comparação entre os dois meses para cada empresa.
    df_comp = df_comp.melt(id_vars='Empresa', var_name='Periodo', value_name='Acessos') # Realiza o processo de unpivot (melt) para transformar os dados de formato largo para formato longo, onde cada linha representa uma combinação única de empresa e período, com a coluna 'Acessos' contendo os valores correspondentes, facilitando a visualização e análise comparativa entre os períodos.
    top_10_empresas = (dfcrescimento.iloc[-1] - dfcrescimento.iloc[-2]).nlargest(10).index # Identifica as 10 empresas com maior crescimento absoluto entre os dois últimos meses, calculando a diferença de acessos entre o mês atual e o mês anterior para cada empresa, e selecionando as 10 maiores variações positivas para destacar as empresas que tiveram o maior aumento em acessos no período analisado.
    df_comp = df_comp[df_comp['Empresa'].isin(top_10_empresas)] # Filtra o DataFrame para incluir apenas as 10 empresas com maior crescimento absoluto, garantindo que a visualização comparativa se concentre nas empresas mais relevantes em termos de crescimento no período analisado.
    ordem_empresas = df_comp[df_comp['Periodo'] == mes_atual].sort_values(by='Acessos', ascending=True)['Empresa'].tolist() # Define a ordem das empresas para a visualização, ordenando as empresas com base no número de acessos no mês atual, garantindo que a visualização seja organizada de forma a destacar as empresas com maior número de acessos no período mais recente.
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
    top_pct['Crescimento %'] = top_pct['Crescimento %'].round(2)
    fig3 = px.bar(top_pct, x='Crescimento %', y='Empresa', orientation='h',
                  title="Top 10: Maior Crescimento Percentual (Volume > 1000)",
                  color='Crescimento %', text_auto='%.2%')

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
    st.title("Painel de Inteligência Estratégica")
    
    # --- 1. PROCESSAMENTO DOS DADOS ---
    # Agrupamento para métricas de crescimento
    df_pivot = df.pivot_table(index=['Empresa', 'Grupo Econômico', 'Porte da Prestadora'], 
                             columns='periodo', values='acessos', aggfunc='sum', fill_value=0)
    
    mes_atual = df_pivot.columns[-1]
    mes_ant = df_pivot.columns[-2]
    
    df_pivot['Crescimento %'] = ((df_pivot[mes_atual] - df_pivot[mes_ant]) / df_pivot[mes_ant] * 100).fillna(0)
    df_pivot['Volume Atual'] = df_pivot[mes_atual]
    df_pivot = df_pivot.reset_index()

    # --- 2. LAYOUT: PERFORMANCE E AGRESSIVIDADE ---
    st.header("1. Performance & Agressividade Competitiva")
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        mais_agressivo = df_pivot.nlargest(1, 'Crescimento %')
        st.metric("Líder em Agressividade", mais_agressivo['Empresa'].values[0], 
                  f"{mais_agressivo['Crescimento %'].values[0]:.1f}% MoM")
        
        st.write("---")
        st.markdown("**Insight:** As MVNOs (Telecall, Connect, Emnify) dominam o crescimento percentual, enquanto as 'Big 3' focam em sustentação de base.")

    with c2:
        fig_scatter = px.scatter(df_pivot, x='Volume Atual', y='Crescimento %', 
                                 size='Volume Atual', color='Empresa', hover_name='Empresa',
                                 log_x=True, title="Matriz: Volume (Tamanho) vs Agressividade (Velocidade)",
                                 template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 3. LAYOUT: TERRITÓRIO E RADAR DE PRODUTO ---
    st.header("2. Território e Radar de Produto")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Oportunidade por Porte em cada UF")
        df_uf = df.groupby(['UF', 'Porte da Prestadora'])['acessos'].sum().reset_index()
        fig_bar = px.bar(df_uf, x='UF', y='acessos', color='Porte da Prestadora', 
                        barmode='stack', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_b:
        st.subheader("Radar Tecnológico (Onde apostam?)")
        df_tech = df.groupby(['Grupo Econômico', 'Tecnologia Geração'])['acessos'].count().reset_index()
        fig_heat = px.density_heatmap(df_tech, x='Tecnologia Geração', y='Grupo Econômico', z='acessos',
                                      color_continuous_scale="Viridis", template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- 4. RESPOSTA DIRETA ÀS PERGUNTAS ---
    with st.expander("📝 Ver Resumo Estratégico (Respostas às Perguntas)"):
        st.markdown("""
        * **Agressividade:** Identificada principalmente em players de nicho (MVNOs). A Telecall e a Connect lideram o ritmo de aquisição de novos acessos.
        * **Radar de Produtos:** O mapa de calor tecnológico revela quais grupos econômicos estão alocando base em tecnologias de nova geração. Se um concorrente menor cresce em uma tecnologia que a Connect não atua, ele deve ser prioridade no radar.
        * **Avanço de Menores:** O gráfico de barras por 'Porte da Prestadora' por UF mostra claramente que em estados onde o 'Pequeno Porte' tem maior fatia, há menor barreira de entrada e maior oportunidade para a Connect crescer.
        """)
def inteligencia_competitiva():
    st.header("📍 Inteligência Territorial")
    
    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        ufs = st.multiselect("Filtrar por UF:", df['UF'].unique(), default=df['UF'].unique())
    with col_f2:
        tech = st.multiselect("Filtrar por Empresas:", df['Empresa'].unique(), default=df['Empresa'].unique())
    
    df_f = df[(df['UF'].isin(ufs)) & (df['Empresa'].isin(tech))]
    
    # KPIs Rápidos
    c1, c2 = st.columns(2)

    with c1:
        # Gráfico de Boxplot: Comparação de dispersão de acessos por UF
        st.subheader("1. Como o mercado se comporta por tipo de pessoa?")
        df_box = df_f.groupby(['Tipo de Pessoa', 'UF', 'Empresa'])['acessos'].sum().reset_index()
        
        fig_box = px.box(
        df_box, 
        x='Tipo de Pessoa', 
        y='acessos', 
        color='Empresa', 
        title="Distribuição de Volume de Acessos por Tipo de Pessoa e Empresas",
        template="plotly_dark",
        points="all",
        # O hover_data aceita uma lista das colunas que você quer exibir
        hover_data=['UF', 'acessos'] # Inclui UF e, opcionalmente, o Município
        )

        # Opcional: Melhora o layout para garantir que o hover seja legível
        fig_box.update_layout(
            hovermode="closest"
        )

        st.plotly_chart(fig_box, use_container_width=True)
        st.warning("""
        **Como interpretar:**
        * Observe a mediana (linha dentro da caixa) para entender o volume típico de acessos por tipo de pessoa.
        * Compare a dispersão (tamanho da caixa e extensão dos bigodes) para comparar a variabilidade entre os tipos de pessoa e empresas.
        """)

    with c2:
        # 2. OPORTUNIDADES POR REGIÃO
        st.subheader("2. Onde existem oportunidades de crescimento?")
        
        # Cruzamos UF com crescimento dos players menores
        df_regiao = df_f.groupby(['UF', 'Empresa'])['acessos'].sum().unstack(fill_value=0)
        # Identificamos UFs onde players menores estão crescendo mais que a média
        st.write("Análise sugerida: UFs onde a Connect tem baixa penetração mas o mercado de IoT está em expansão.")
        
        # Gráfico de Matriz de Maturação (Oportunidade)
        # Criamos um dataframe resumo por UF
        df_maturacao = df_f.groupby('UF').agg({'acessos': 'sum', 'Empresa': 'nunique'}).reset_index()
        fig_mat = px.scatter(df_maturacao, x='acessos', y='Empresa', size='acessos', 
                            color='UF', title="Matriz de Maturação por UF (Volume vs Concorrência)",
                            template="plotly_dark")
        st.plotly_chart(fig_mat, use_container_width=True)
        
        st.warning("""
        **Como interpretar:**
        * **Quadrante Inferior Direito (Alto Volume, Baixa Concorrência):** Oportunidade de expansão massiva.
        * **Quadrante Superior Direito (Alto Volume, Alta Concorrência):** Mercado saturado; requer diferenciação de produto.
        """)
    
def competitividade():
    st.header("🎯 Radar Competitivo & Nichos")
    
    empresa_selecionada = st.selectbox("Selecione sua empresa para comparação:", df['Empresa'].unique())
    
    # Análise de Agressividade (Radar Chart)
    st.subheader("Radar de Perfil Competitivo")
    # Agrupamos por métricas que definem "agressividade"
    radar_data = df.groupby('Empresa').agg({
        'Tecnologia Geração': 'nunique', 
        'Tipo de Produto': 'nunique',
        'CNPJ': 'count'
    }).reset_index()
    
    # Normalizando para o Radar (0-1)
    for col in radar_data.columns[1:]:
        radar_data[col] = radar_data[col] / radar_data[col].max()
        
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_data[radar_data['Empresa'] == empresa_selecionada].values[0][1:],
        theta=['Geração Tech', 'Diversidade Produto', 'Market Share'],
        fill='toself', name=empresa_selecionada
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), template="plotly_dark")
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Análise de MVNOs / Pequeno Porte
    st.subheader("Performance de Players de Pequeno Porte (Nichos)")
    pequenos = df[df['Porte da Prestadora'] == 'Pequeno Porte']
    fig_bar = px.bar(pequenos.groupby('Tipo de Produto')['Empresa'].count().reset_index(), 
                     x='Tipo de Produto', y='Empresa', color='Tipo de Produto',
                     title="Foco de Atuação de MVNOs", template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

def visao_geral_page():

    st.title("📈 Visão Geral do Mercado")
    st.subheader("Análise Macroeconômica e Evolução Histórica de Acessos")
    st.markdown("---")

    fig1, fig2, fig3 = crescimento(df)

    st.title("Mercado - Acessos Móveis")

    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)
paginas = [
    st.Page(visao_geral_page, title="Visão Geral do Mercado", icon="📈"),
    st.Page(inteligencia_competitiva, title='Visão Regional', icon="🌍"),
    st.Page(competitividade, title='Radar de Competitividade', icon="📊"),
    st.Page(teste, title='Performance & Agressividade', icon="🔍")
]


navegacao = st.navigation(paginas)
navegacao.run()