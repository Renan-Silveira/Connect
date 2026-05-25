import streamlit as st # Biblioteca para criar interfaces web interativas de forma simples e rápida
import pandas as pd # Biblioteca para manipulação e análise de dados, especialmente útil para trabalhar com DataFrames
import numpy as np # Biblioteca para computação científica, fornece suporte para arrays e operações matemáticas avançadas
import os # Biblioteca para interagir com o sistema operacional, útil para manipulação de arquivos e diretórios
from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
import plotly.express as px # Biblioteca para criar gráficos interativos
import plotly.graph_objects as go # Biblioteca para criar gráficos interativos mais personalizados 

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv() #carrega o ambiente do .env
st.set_page_config( #configuração das páginas do Streamlit, definindo título, ícone, layout e estado inicial da barra lateral
    page_title="Intel de Mercado - Connect/Virtueyes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #000c1f; }
    .stMetric { background-color: #001a3d; padding: 20px; border-radius: 12px; border-left: 5px solid #d4ff00; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    h1, h2, h3 { color: #ffffff; font-family: 'Urbanist', sans-serif; }
    </style>
    """, unsafe_allow_html=True) #adicionando estilo personalizado

# --- CARREGAMENTO DE DADOS ---
@st.cache_data #decorador para cachear os dados carregados, evitando recarregamentos desnecessários e melhorando a performance da aplicação
def carregar_dados(): # Função para carregar os dados do arquivo Parquet, aplicando otimizações de memória e filtragem de colunas para melhorar a performance da aplicação
    DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED", ".")  #diretorio do arquivo pré processado.
    try:
        # 1. Defina apenas as colunas que as páginas realmente utilizam
        colunas_necessarias = [
            'periodo', 'Empresa', 'acessos', 'UF', 
            'Tecnologia Geração', 'Porte da Prestadora', 
            'Tipo de Produto', 'Modalidade de Cobrança'
        ] #lista das colunas usadas
        
        # 2. Leia apenas as colunas filtradas
        df = pd.read_parquet( 
            os.path.join(DIR_DATAPROCESSED, "preprocessado.parquet"),
            columns=colunas_necessarias
        ) #lendo o arquivo parquet
        
        # 3. converte a data adequadamente
        if 'periodo' in df.columns:
            df['periodo'] = pd.to_datetime(df['periodo'])
            
        # 4. Transforma strings repetitivas em categorias
        colunas_categoricas = [
            'Empresa', 'UF', 'Tecnologia Geração', 
            'Porte da Prestadora', 'Tipo de Produto', 'Modalidade de Cobrança'
        ]
        for col in colunas_categoricas:
            if col in df.columns:
                df[col] = df[col].astype('category') #formatando colunas em categoricas
                
        # 5. convertendo as colunas númericas em valores mais leves
        if 'acessos' in df.columns:
            df['acessos'] = pd.to_numeric(df['acessos'], downcast='float')
            
        return df
    except Exception as e: #captura qualquer exceção 
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados() #chama a função de carregar os dados

# --- PÁGINA 1: VISÃO MACRO ---
def visao_geral_page():
    st.title("📈 Crescimento do Mercado Móvel") #título da página
    
    if df.empty: return 

    # preparando os dados de crescimento
    dfcrescimento = df.groupby(['periodo', 'Empresa'])['acessos'].sum().unstack(fill_value=0)
    atual = dfcrescimento.iloc[-1]
    anterior = dfcrescimento.iloc[-2]
    
    # principais métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Acessos (Mês Atual)", f"{atual.sum()/1e6:.2f}M", f"{((atual.sum() - anterior.sum()) / anterior.sum()) * 100:.2f}% MoM") #calculado a variação percentual
    
    empresa_alvo = "Connect Iot Solutions Ltda"
    crescimento_medio_empresas = dfcrescimento.pct_change().iloc[-1].mean() * 100 # Crescimento médio percentual de todas as empresas no último período
    empresas_crescendo = (dfcrescimento.iloc[-1] > dfcrescimento.iloc[-2]).sum() # Número de empresas que tiveram crescimento no último período
    total_empresas = len(dfcrescimento.columns) # Total de empresas no dataset
    val_connect = atual.get(empresa_alvo, 0)  
    var_connect = ((val_connect - anterior.get(empresa_alvo, 0)) / anterior.get(empresa_alvo, 1)) * 100 if anterior.get(empresa_alvo, 0) != 0 else 0 # Variação percentual da Connect, evitando divisão por zero
    c2.metric("Acessos Connect", f"{val_connect:,.0f}", f"{var_connect:.1f}%") # Métrica específica para a Connect, mostrando o número de acessos e a variação percentual em relação ao período anterior
    c3.metric(label="Empresas em Expansão", value=f"{empresas_crescendo} de {total_empresas}", delta=f"{ (empresas_crescendo/total_empresas)*100:.0f}% do market cap", delta_color="normal") #Métrica de expansão
    c4.metric(label="Velocidade Média (Empresas)", value=f"{crescimento_medio_empresas:.2f}%", help="Média de crescimento percentual de todas as empresas no período.") #Métrica de velocidade de crescimento
    # P1: Crescimento do mercado nos últimos meses
    mercado_total = (
    dfcrescimento
    .sum(axis=1)
    .reset_index(name='Total Acessos')
    ) #criando o dataframe de acessos agrupado

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
        go.Scatter(x=mercado_total['periodo'], y=mercado_total['Total Acessos'], mode='lines+markers', name='Total Acessos', line=dict(width=3), hovertemplate='<b>%{x|%m/%Y}</b><br>' +'Acessos: %{y:,.0f}<extra></extra>'))

    # Média móvel
    fig1.add_trace(
        go.Scatter(x=mercado_total['periodo'], y=mercado_total['MM3'], mode='lines', name='Média móvel (3)', line=dict(dash='dash')))

    # Destaque pico
    fig1.add_trace(
        go.Scatter(x=[pico['periodo']], y=[pico['Total Acessos']], mode='markers+text', text=['Pico'], textposition='top center', marker=dict(size=12), name='Pico'))

    # Destaque mínimo
    fig1.add_trace(
        go.Scatter(x=[minimo['periodo']], y=[minimo['Total Acessos']], mode='markers+text', text=['Mínimo'], textposition='bottom center', marker=dict(size=12), name='Mínimo'))

    # Layout
    fig1.update_layout( title='Evolução do Mercado de Acessos Móveis', xaxis_title='Período', yaxis_title='Total de Acessos', hovermode='x unified', template='plotly_white', height=600, legend_title='Indicadores')

    # Anotação último valor
    fig1.add_annotation(x=ultimo_valor['periodo'], y=ultimo_valor['Total Acessos'],
        text=(
            f"Último:<br>"
            f"{ultimo_valor['Total Acessos']:,.0f}<br>"
            f"{ultimo_valor['Crescimento %']:.2f}%"), showarrow=True, arrowhead=2)

    
    fig1.update_yaxes(tickformat=',.0f') # Formatação eixo Y
    st.plotly_chart(fig1, width='stretch')

    colA, colB = st.columns(2)
    # Plot 2: Maior crescimento absoluto
    with colA:
        top_abs = (atual - anterior).nlargest(10).reset_index()
        top_abs.columns = ['Empresa', 'Crescimento Absoluto']
        fig2 = px.bar(top_abs, x='Crescimento Absoluto', y='Empresa', orientation='h', title="Top 10: Crescimento Absoluto (MoM)", text_auto='.2s', template="plotly_dark")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, width='stretch')

    # Plot3: Maior crescimento percentual
    with colB:
        filtro_vol = atual > 1000 # Filtro de ruído
        top_pct = ((atual[filtro_vol] - anterior[filtro_vol]) / anterior[filtro_vol] * 100).nlargest(10).reset_index()
        top_pct.columns = ['Empresa', 'Crescimento %']
        fig3 = px.bar(top_pct, x='Crescimento %', y='Empresa', orientation='h', title="Top 10: Crescimento Percentual (Vol > 1k)", text_auto='.1f', template="plotly_dark")
        fig3.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, width='stretch')


# --- PÁGINA 2: AGRESSIVIDADE E POSICIONAMENTO---
def posicionamento_agressividade_page():
    st.title("⚔️ Posicionamento e Agressividade")
    
    if df.empty: return

    meses = sorted(df['periodo'].unique())
    if len(meses) < 2:
        st.warning("Necessário pelo menos dois meses de dados para analisar crescimento.")
        return
        
    df_atual = df[df['periodo'] == meses[-1]]
    df_ant = df[df['periodo'] == meses[-2]]

    vol_atual = df_atual.groupby('Empresa')['acessos'].sum()
    vol_ant = df_ant.groupby('Empresa')['acessos'].sum()
    
    cresc_pct = ((vol_atual - vol_ant) / vol_ant * 100).fillna(0)
    
    df_matriz = pd.DataFrame({'Volume': vol_atual, 'Crescimento %': cresc_pct}).reset_index()
    df_matriz = df_matriz[df_matriz['Volume'] > 500] # Limpando outliers pequenos

    # Plot 6: Comportamento agressivo (Matriz Volume x Velocidade)
    fig_scatter = px.scatter(
        df_matriz, x='Volume', y='Crescimento %', size='Volume', color='Empresa', 
        hover_name='Empresa', log_x=True, 
        title="Matriz de Agressividade: Volume vs Velocidade de Crescimento (Log Scale)",
        template="plotly_dark"
    )
    # Adicionando linhas de quadrante (médias)
    fig_scatter.add_hline(y=df_matriz['Crescimento %'].median(), line_dash="dash", annotation_text="Mediana de Crescimento")
    fig_scatter.add_vline(x=df_matriz['Volume'].median(), line_dash="dash")
    st.plotly_chart(fig_scatter, width='stretch')

    # Plot 4: Como a Connect se posiciona (Market Share)
    st.subheader("Market Share de Tecnologias - Connect vs Mercado")
    c1, c2 = st.columns(2)
    with c1:
        # Market Share Total
        top5 = vol_atual.nlargest(5).index.tolist()
        df_atual['Agrupamento'] = df_atual['Empresa'].apply(lambda x: x if x in top5 or 'Connect' in x else 'Outros')
        fig_share = px.pie(df_atual, values='acessos', names='Agrupamento', title="Market Share Atual", hole=0.4, template="plotly_dark")
        st.plotly_chart(fig_share, width='stretch')
    with c2:
        # Portfólio Tecnológico da Connect vs Lider
        empresas_comp = st.multiselect("Comparar portfólio tecnológico:", df['Empresa'].unique(), default=[top5[0], "Connect Iot Solutions Ltda" if "Connect Iot Solutions Ltda" in df['Empresa'].unique() else top5[1]])
        df_comp = df_atual[df_atual['Empresa'].isin(empresas_comp)]
        fig_tech = px.histogram(df_comp, x='Empresa', y='acessos', color='Tecnologia Geração', barmode='group', title="Mix Tecnológico Atual", template="plotly_dark")
        st.plotly_chart(fig_tech, width='stretch')


# --- PÁGINA 3: OPORTUNIDADES E NICHOS ---
def radar_oportunidades_page():
    st.title("🎯 Oportunidades, Radar e Nichos")    
    if df.empty: return

    df_atual = df[df['periodo'] == df['periodo'].max()]

    # Plot 5: Oportunidades de crescimento por UF
    st.subheader("Oportunidades Territoriais (Saturação por UF)")
    df_uf = df_atual.groupby('UF').agg({'acessos': 'sum', 'Empresa': 'nunique'}).reset_index()
    fig_uf = px.scatter(df_uf, x='acessos', y='Empresa', color='UF', size='acessos', text='UF',
                        title="Matriz de Maturação por UF (Volume x Competição)", template="plotly_dark")
    fig_uf.update_traces(textposition='top center')
    st.plotly_chart(fig_uf, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        # Plot 7: Radar de acompanhamento de Produtos (Tecnologia Geração vs Empresas)
        st.subheader("Radar de Produtos (Apostas Tecnológicas)")
        df_radar = df_atual.groupby(['Empresa', 'Tecnologia Geração'])['acessos'].sum().reset_index()
        # Pegando top 15 empresas para não poluir o mapa
        top_empresas = df_atual.groupby('Empresa')['acessos'].sum().nlargest(15).index
        df_radar = df_radar[df_radar['Empresa'].isin(top_empresas)]
        fig_heat = px.density_heatmap(df_radar, x='Tecnologia Geração', y='Empresa', z='acessos', title="Mapa de Calor: Foco Tecnológico", template="plotly_dark", color_continuous_scale="Viridis")
        st.plotly_chart(fig_heat, width='stretch')

    with col2:
        # Plot 8: Avanço de Players Menores / MVNOs (Porte x Modalidade/Produto)
        st.subheader("Avanço de Players Menores (MVNOs)")
        # Analisando o avanço pelo tipo de cobrança e produto
        df_mvno = df_atual[df_atual['Porte da Prestadora'] == 'Pequeno Porte']
        fig_mvno = px.sunburst(df_mvno, path=['Tipo de Produto', 'Modalidade de Cobrança', 'Empresa'], values='acessos', title="Atuação de Pequeno Porte (Nichos de Produtos)", template="plotly_dark")
        st.plotly_chart(fig_mvno, width='stretch')


# --- PÁGINA 4: RECOMENDAÇÕES EXECUTIVAS ---
def recomendacoes_page():
    st.title("💡 Insights e Recomendações Estratégicas")    
    # Simulação de geração de insights dinâmicos baseados no df
    df_atual = df[df['periodo'] == df['periodo'].max()]
    lider = df_atual.groupby('Empresa')['acessos'].sum().idxmax()
    mvnos_crescimento = "Alto" # Lógica simplificada para texto
    
    st.markdown("### 🔍 Insights Gerados")
    st.markdown(f"""
    * **Liderança Consolidada vs Crescimento Periférico:** A `{lider}` mantém o maior volume, mas a análise de matriz de agressividade mostra que os players de 'Pequeno Porte' estão tracionando acessos a taxas percentuais muito superiores.
    * **Foco Tecnológico das MVNOs:** O mapa de calor e o detalhamento de nichos indicam que os players menores estão se especializando em nichos específicos de `Tipo de Produto` (ex: M2M/IoT B2B) onde as grandes telcos têm atendimento mais engessado.
    * **Territórios Inexplorados:** O gráfico de saturação por UF revela estados onde há volume de mercado, mas baixa fragmentação de concorrentes, representando oceanos azuis para a entrada comercial da Connect.
    """)

    st.markdown("### 📋 Recomendações para Estratégia de Produto e Mercado")
    c1, c2 = st.columns(2)
    with c1:
        st.success("**Estratégia de Produto**")
        st.markdown("""
        1. **Monitoramento Ativo:** O Radar de Produtos mostra novas tecnologias ganhando tração. A Connect deve avaliar o custo-benefício de espelhar as ofertas de MVNOs agressivas no quadrante superior esquerdo.
        2. **Pacotização Segmentada:** Avaliar a `Modalidade de Cobrança` dominante no B2B. A flexibilidade no modelo de cobrança tem sido a principal arma de players de nicho para ganho de base.
        """)
    with c2:
        st.warning("**Estratégia de Mercado**")
        st.markdown("""
        1. **Ataque Regionalizado:** Redirecionar os esforços de marketing e vendas para os UFs localizados no Quadrante Inferior Direito da matriz (Alta Oportunidade, Baixa Concorrência de nicho).
        2. **Benchmarking Competitivo:** Colocar as top 3 empresas de *Maior Crescimento Percentual* em um radar mensal de GTM para engenharia reversa de suas estratégias de precificação.
        """)


# --- NAVEGAÇÃO ---
paginas = [
    st.Page(visao_geral_page, title="1. Visão Macro do Mercado"),
    st.Page(posicionamento_agressividade_page, title="2. Posicionamento e Agressividade"),
    st.Page(radar_oportunidades_page, title="3. Oportunidades e Nichos"),
    st.Page(recomendacoes_page, title="4. Insights e Recomendações")
]

navegacao = st.navigation(paginas)
navegacao.run()