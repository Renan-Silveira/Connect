# connect
Solução de Business Intelligence e pipeline de dados para análise de mercado, concorrência e expansão de acessos móveis M2M no Brasil, utilizando dados da Anatel.


# 📡 Análise de Mercado IoT e Conectividade Móvel (M2M)

## 📌 Visão Geral
Este repositório contém a solução desenvolvida para o Case Técnico de Business Intelligence. O objetivo principal é apoiar a estratégia comercial e de produtos da *Connect*, construindo uma visão analítica detalhada do mercado brasileiro de acessos móveis com base em dados públicos da Anatel.

A solução abrange desde a coleta e tratamento dos dados brutos até a modelagem e criação de um dashboard executivo para acompanhamento de métricas-chave.

## 🎯 Objetivos de Negócio
O dashboard e as análises geradas buscam responder às seguintes perguntas estratégicas:
* Qual o crescimento do mercado de acessos móveis (M2M) nos últimos meses?
* Quais prestadoras tiveram maior crescimento absoluto e percentual?
* Como a Connect se posiciona frente aos concorrentes diretos?
* Em quais UFs, regiões ou tecnologias existem as maiores oportunidades de expansão?
* Quais players demonstram comportamento agressivo e devem entrar no radar da área de Produtos?

## 🗄️ Fonte de Dados
Os dados foram extraídos dos painéis públicos da **Agência Nacional de Telecomunicações (Anatel)**.
* **Link da fonte:** [Painéis de Dados - Acessos Telefonia Móvel](https://informacoes.anatel.gov.br/paineis/acessos/telefonia-movel)
* **Filtro Aplicado:** Tipo de Produto focado exclusivamente em **M2M** (Machine to Machine).

## 🛠️ Arquitetura e Tecnologias Utilizadas
A stack foi escolhida visando reprodutibilidade, governança e clareza na manipulação dos dados:
* **Extração e Tratamento (ETL):** Python / Pandas
* **Armazenamento / Base Analítica:** Arquivos Pickle
* **Visualização de Dados:** Streamlit
* **Controle de Versão:** Git & GitHub

## 📂 Estrutura do Repositório
```text
├── data/
│   ├── raw/               # Arquivos brutos baixados da Anatel
│   └── processed/         # Base analítica tratada e padronizada
├── notebooks/             # Notebooks de exploração e validação de dados
├── src/                   # Scripts Python para extração e pipeline ETL
├── dashboard/             # código do Streamlit
├── docs/                  # Apresentação final e materiais complementares
├── requirements.txt       # Pacotes python usados para a elaboração do projeto
└── README.md
