# CONNECT

Solução de Business Intelligence e pipeline de dados para análise de mercado, concorrência e expansão de acessos móveis M2M no Brasil, utilizando dados públicos da Anatel.

---

# Análise de Mercado IoT e Conectividade Móvel (M2M)

## Visão Geral

Este repositório contém a solução desenvolvida para o Case Técnico de Business Intelligence. O objetivo principal é apoiar a estratégia comercial e de produtos da *Connect*, construindo uma visão analítica detalhada do mercado brasileiro de acessos móveis com base em dados públicos da Anatel.

A solução contempla:

* Extração automatizada dos dados públicos da Anatel;
* Conversão e padronização dos arquivos CSV para Parquet;
* Tratamento e modelagem analítica dos dados;
* Criação de uma camada analítica otimizada para dashboards;
* Geração de indicadores de crescimento do mercado M2M;
* Consumo dos dados via Streamlit.

O pipeline foi desenvolvido com foco em:

* Performance;
* Reprodutibilidade;
* Governança;
* Escalabilidade;
* Organização em camadas analíticas.

---

# Objetivos de Negócio

O dashboard e as análises geradas buscam responder às seguintes perguntas estratégicas:

* Qual o crescimento do mercado de acessos móveis (M2M) nos últimos meses?
* Quais prestadoras tiveram maior crescimento absoluto e percentual?
* Como a Connect se posiciona frente aos concorrentes diretos?
* Em quais UFs, regiões ou tecnologias existem as maiores oportunidades de expansão?
* Quais players demonstram comportamento agressivo e devem entrar no radar da área de Produtos?

---

# Fonte de Dados

Os dados foram extraídos dos painéis públicos da Agência Nacional de Telecomunicações (Anatel).

## Fonte Oficial

* Painéis de Dados — Telefonia Móvel

Filtro aplicado:

* Tipo de Produto = M2M (Machine to Machine)

Os dados contemplam:

* Prestadoras;
* Municípios;
* UF;
* Tecnologias;
* Grupo econômico;
* Modalidade de cobrança;
* Quantidade de acessos;
* Evolução temporal do mercado.

---

# Arquitetura da Solução

```text
               ┌────────────────────┐
               │ Dados Abertos      │
               │ ANATEL             │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ extract.py         │
               │ Download + unzip   │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ rename_csv.py      │
               │ Padronização nomes │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ rename_parquet.py  │
               │ CSV → Parquet      │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ compile.py         │
               │ Modelagem analítica│
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ growth.py          │
               │ Camada GOLD        │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │ Dashboard           │
               │ Streamlit           │
               └────────────────────┘
```

---

# Tecnologias Utilizadas

| Tecnologia | Finalidade                                     |
| ---------- | ---------------------------------------------- |
| Python     | Pipeline ETL                                   |
| Pandas     | Manipulação de dados                           |
| Polars     | Processamento performático de arquivos Parquet |
| PyArrow    | Leitura e escrita de arquivos analíticos       |
| Streamlit  | Dashboard e visualização                       |
| Parquet    | Armazenamento analítico                        |
| Git/GitHub | Versionamento                                  |
| dotenv     | Gerenciamento de variáveis de ambiente         |

---

# Estrutura do Repositório

```text
├── data/
│   ├── raw/               # Arquivos brutos extraídos da Anatel
│   ├── parquet/           # Arquivos convertidos para parquet
│   ├── processed/         # Base consolidada e tratada
│   └── gold/              # Camada analítica otimizada para dashboard
│
├── notebooks/             # Estudos exploratórios e validações
├── src/                   # Pipeline ETL
├── dashboard/             # Dashboard Streamlit
├── docs/                  # Materiais complementares
├── requirements.txt       # Dependências do projeto
└── README.md
```

---

# Estrutura do Arquivo `.env`

```env
DIR_DATARAW=data/raw
DIR_DATAPARQUET=data/parquet
DIR_DATAPROCESSED=data/processed
DIR_DATA=data
DIR_NOTEBOOKS=notebooks
DIR_SRC=src
DIR_DASHBOARD=dashboard
DIR_DOCS=docs
DIR_GOLD=data/gold

URL=https://...
NOME_FILE=download.zip
```

---

# Pipeline ETL

A pipeline foi organizada em etapas independentes e reutilizáveis.

## Fluxo Geral

```text
Extração → Padronização → Conversão → Consolidação → Camada GOLD
```

---

# Documentação dos Arquivos

## `flow.py`

Arquivo principal responsável por orquestrar toda a execução da pipeline ETL.

### Responsabilidades

* Controlar a ordem de execução das etapas;
* Registrar logs de execução;
* Interromper a pipeline em caso de erro;
* Garantir rastreabilidade do processo.

### Ordem de Execução

```python
extract()
rename_csv()
rename_parquet()
compile_parquet()
growth()
```

### Como executar

```bash
python flow.py
```

---

## `extract.py`

Responsável por realizar o download automático dos dados da Anatel.

### Funcionalidades

* Download do arquivo ZIP;
* Barra de progresso utilizando `tqdm`;
* Controle de timeout;
* Tratamento de erros;
* Extração automática dos arquivos;
* Registro de logs de falha.

### Entrada

Arquivo configurado na variável:

```env
URL
```

### Saída

```text
/data/raw
```

### Principais bibliotecas utilizadas

* requests
* zipfile
* tqdm
* logging

---

## `rename_csv.py`

Responsável pela padronização dos nomes dos arquivos CSV extraídos.

### Objetivo

Os arquivos baixados da Anatel possuem prefixos extensos e inconsistentes. O script remove partes desnecessárias do nome para facilitar a organização e processamento posterior.

### Exemplo

Antes:

```text
Acessos_Telefonia_Movel_2020-1S_colunas.csv
```

Depois:

```text
2020-1S_colunas.csv
```

### Saída

Arquivos renomeados dentro de:

```text
/data/raw
```

---

## `rename_parquet.py`

Responsável pela conversão dos arquivos CSV para o formato Parquet.

### Funcionalidades

* Leitura dos CSVs usando PyArrow;
* Conversão para formato colunar Parquet;
* Compressão `snappy`;
* Remoção automática do CSV após conversão.

### Benefícios do uso de Parquet

* Melhor performance de leitura;
* Menor espaço em disco;
* Melhor integração com engines analíticas.

### Entrada

```text
/data/raw
```

### Saída

```text
/data/parquet
```

### Principais bibliotecas

* pyarrow.csv
* pyarrow.parquet

---

## `compile.py`

Responsável pela consolidação e transformação analítica dos arquivos Parquet.

Este é o principal arquivo de modelagem da pipeline.

### Funcionalidades

* Leitura lazy utilizando Polars;
* Filtro apenas para registros M2M;
* Padronização de CNPJ;
* Conversão de períodos;
* Criação de colunas de ano e mês;
* Transformação de colunas temporais em linhas (`unpivot`);
* Consolidação de múltiplos arquivos;
* Geração da base analítica final.

### Regras de Negócio

#### Filtro de Produto

Apenas registros com:

```text
Tipo de Produto = M2M
```

#### Filtro Temporal

Somente arquivos a partir de:

```text
2020+
```

### Transformações realizadas

| Transformação       | Objetivo                                 |
| ------------------- | ---------------------------------------- |
| Unpivot             | Estruturar períodos em formato analítico |
| Fill Null           | Evitar valores nulos                     |
| Cast Int32          | Otimização de memória                    |
| zfill(14)           | Padronização do CNPJ                     |
| Extração de ano/mês | Facilitar análises temporais             |

### Entrada

```text
/data/parquet
```

### Saída

```text
/data/processed/preprocessado.parquet
```

### Principais bibliotecas

* polars
* glob
* dotenv

---

## `growth.py`

Responsável pela criação da camada GOLD.

### Objetivo

Criar uma visão otimizada contendo apenas os últimos 12 meses de dados.

### Funcionalidades

* Leitura do dataset consolidado;
* Aplicação de filtro temporal;
* Geração de dataset analítico enxuto;
* Exportação da camada GOLD.

### Regra aplicada

```text
Últimos 365 dias
```

### Entrada

```text
/data/processed/preprocessado.parquet
```

### Saída

```text
/data/gold/gold_growth.parquet
```

# Camadas de Dados

## RAW

Dados brutos extraídos diretamente da Anatel.

```text
/data/raw
```

---

## PARQUET

Arquivos convertidos para formato colunar otimizado.

```text
/data/parquet
```

---

## PROCESSED

Base consolidada, tratada e modelada.

```text
/data/processed
```

---

## GOLD

Camada analítica final consumida pelo dashboard.

```text
/data/gold
```

---

# Como Instalar as Dependências

## 1. Criar ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Como Executar o Projeto

## Executar pipeline completa

```bash
python flow.py
```

---

## Executar etapas individualmente

### Download dos dados

```bash
python extract.py
```

### Renomear CSVs

```bash
python rename_csv.py
```

### Converter CSV → Parquet

```bash
python rename_parquet.py
```

### Consolidar base analítica

```bash
python compile.py
```

### Gerar camada GOLD

```bash
python growth.py
```

---

# Estrutura Analítica Final

O dataset final possui informações como:

| Coluna          | Descrição                   |
| --------------- | --------------------------- |
| CNPJ            | Identificador da prestadora |
| Empresa         | Nome da operadora           |
| UF              | Unidade Federativa          |
| Município       | Município                   |
| Tecnologia      | Tecnologia utilizada        |
| Grupo Econômico | Grupo empresarial           |
| periodo         | Competência do dado         |
| acessos         | Quantidade de acessos       |
| ano             | Ano da competência          |
| mes             | Mês da competência          |

---

Indicadores esperados:

* Crescimento absoluto;
* Crescimento percentual;
* Participação de mercado;
* Evolução temporal;
* Comparativo entre operadoras;
* Análise regional;
* Distribuição tecnológica.
