def compile_parquet():
    # Este arquivo foi pensado para compilar os arquivos parquet gerados no processo para um arquivo préprocessado.
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
    import glob # Biblioteca para encontrar arquivos e diretórios usando padrões de correspondência de nomes
    import pandas as pd # Biblioteca para manipulação de dados, usada para ler e escrever arquivos Parquet usando pandas
    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    DIR_DATAPARQUET = os.getenv("DIR_DATAPARQUET") # Obtém o diretório onde os arquivos Parquet estão localizados a partir das variáveis de ambiente
    DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED") # Obtém o diretório onde o arquivo pré-processado será salvo a partir das variáveis de ambiente
    padrao = os.path.join(DIR_DATAPARQUET, "[0-9][0-9][0-9][0-9]*_Colunas.parquet")
    try:
        arquivos_parquet = sorted(glob.glob(padrao))  # Encontra todos os arquivos Parquet que correspondem ao padrão especificado usando glob
        arquivos_filtrados = []
        for arquivo in arquivos_parquet:
            nome_arquivo = os.path.basename(arquivo) # Obtém o nome do arquivo a partir do caminho completo usando os.path.basename para garantir portabilidade entre sistemas operacionais
            try:
                ano_arquivo = int(nome_arquivo[:4]) # Extrai os 4 primeiros caracteres e transforma em número
                if ano_arquivo >= 2020:
                    arquivos_filtrados.append(arquivo)
            except ValueError:
                # Caso algum arquivo não comece com número, ele ignora para não quebrar o código
                print(f"Aviso: O arquivo '{nome_arquivo}' não inicia com um ano válido e foi descartado.")
            continue

        arquivos_parquet = arquivos_filtrados # Substitui a lista original pela lista filtrada
        if not arquivos_parquet: # Verifica se a lista de arquivos Parquet está vazia
            print("Nenhum arquivo Parquet encontrado para compilar.") # Imprime uma mensagem indicando que nenhum arquivo Parquet foi encontrado
            return False # Retorna False para indicar que a compilação falhou devido à ausência de arquivos Parquet
        df_final = pd.read_parquet(arquivos_parquet[0]) # Lê o primeiro arquivo Parquet encontrado usando pandas e armazena em um DataFrame chamado df_final, que servirá como base para a compilação dos dados
        colunas = ['CNPJ', 'Código Nacional', 'Município', 'UF', 'Modalidade de Cobrança', 'Tecnologia', 'Tecnologia Geração', 'Empresa', 'Porte da Prestadora', 'Tipo de Pessoa', 'Tipo de Produto', 'Código IBGE Município', 'Grupo Econômico']
        
            
        for arquivo in arquivos_parquet[1:]: # Itera sobre os arquivos Parquet encontrados, começando do segundo arquivo (índice 1) até o final da lista

            df_proximo = pd.read_parquet(arquivo) # Lê o próximo arquivo Parquet usando pandas e armazena em um DataFrame temporário chamado df_proximo
            df_final = pd.merge(df_final, df_proximo, on=colunas, how='outer') # Realiza uma junção externa (outer join) entre o DataFrame final e o próximo DataFrame usando as colunas especificadas como chave de junção, garantindo que todas as linhas de ambos os DataFrames sejam incluídas no resultado final

       
        colunas_periodo = [col for col in df_final.columns if col not in colunas] # Cria uma lista de colunas de período, filtrando as colunas do DataFrame final para incluir apenas aquelas que não estão na lista de colunas especificadas, presumivelmente identificando as colunas que representam os períodos de tempo para os dados de acessos
        for col in colunas: # Itera sobre as colunas especificadas na lista 'colunas' para realizar a conversão de tipo
            df_final[col] = df_final[col].astype('category') # Converte as colunas especificadas para o tipo 'category' usando pandas, o que pode ajudar a reduzir o uso de memória e melhorar o desempenho ao lidar com grandes conjuntos de dados categóricos
        df_final[colunas_periodo] = (df_final[colunas_periodo].astype('float32')) # Converte as colunas de período para o tipo 'float32' usando pandas, o que pode ajudar a reduzir o uso de memória ao lidar com grandes conjuntos de dados numéricos, especialmente se os valores forem decimais ou tiverem uma faixa de valores que se encaixe no tipo 'float32'
        df_long = df_final.melt(
            id_vars=colunas,
            value_vars=colunas_periodo,
            var_name='periodo',
            value_name='acessos'
        )
        df_long['periodo'] = pd.to_datetime(df_long['periodo'], format='%Y-%m') # Converte a coluna 'periodo' para o tipo datetime usando pandas, especificando o formato de data como ano-mês (YYYY-MM) para garantir que os dados de período sejam tratados como datas
        df_long['ano'] = df_long['periodo'].dt.year # Extrai o ano da coluna 'periodo' e armazena em uma nova coluna chamada 'ano' usando pandas, permitindo que os dados sejam analisados por ano
        df_long['mes'] = df_long['periodo'].dt.month # Extrai o mês da coluna 'periodo' e armazena em uma nova coluna chamada 'mes' usando pandas, permitindo que os dados sejam analisados por mês
        df_long['acessos'] = df_long['acessos'].fillna(0).astype('int32') # Preenche os valores nulos na coluna 'acessos' com 0 e converte a coluna para o tipo 'int32' usando pandas, garantindo que os dados de acessos sejam tratados como números inteiros sem valores nulos
        df_long.to_parquet(os.path.join(DIR_DATAPROCESSED, 'preprocessado.parquet'), index=False) # Salva o DataFrame final em formato Parquet no diretório de pré-processamento, sem incluir o índice do DataFrame
        print(f"Compilação concluída. Arquivo pré-processado salvo em: {os.path.join(DIR_DATAPROCESSED, 'preprocessado.parquet')}") # Imprime uma mensagem indicando que a compilação foi concluída e onde o arquivo pré-processado foi salvo
        return True # Retorna True para indicar que a compilação foi concluída com sucesso
    except Exception as e: # Captura qualquer exceção que possa ocorrer durante a compilação dos arquivos Parquet
        print(f"Erro ao compilar arquivos Parquet: {e}") # Imprime uma mensagem de erro caso ocorra um problema durante a compilação dos arquivos Parquet
        return False # Retorna False para indicar que a compilação falhou devido a um erro
    

if __name__ == "__main__":
    compile_parquet() # Chama a função de compilação dos arquivos Parquet quando o script é executado diretamente
