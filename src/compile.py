def compile_parquet():
    # Este arquivo foi pensado para compilar os arquivos parquet gerados no processo para um arquivo préprocessado.
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
    import glob # Biblioteca para encontrar arquivos e diretórios
    import polars as pl # Biblioteca para manipulação de dados usada para processar os arquivos Parquet
    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    DIR_DATAPARQUET = os.getenv("DIR_DATAPARQUET") # Obtém o diretório onde os arquivos Parquet estão localizados
    DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED") # Obtém o diretório onde o arquivo pré-processado vai ser salvo
    padrao = os.path.join(DIR_DATAPARQUET, "[0-9][0-9][0-9][0-9]*_Colunas.parquet") #Importa todos os arquivos com numeros no nome
    try:
        arquivos_parquet = sorted(glob.glob(padrao)) # Encontra todos os arquivos Parquet
        arquivos_filtrados = [] 
        
        for arquivo in arquivos_parquet: # Itera sobre os arquivos encontrados para filtrar apenas aqueles que começam com um ano (4 dígitos) e são maiores ou iguais a 2020
            nome_arquivo = os.path.basename(arquivo) # Obtém apenas o nome do arquivo (sem o caminho) para verificar o ano
            try: 
                if int(nome_arquivo[:4]) >= 2020: 
                    arquivos_filtrados.append(arquivo) # Adiciona o arquivo à lista de arquivos filtrados se o ano for maior ou igual a 2020
            except ValueError: 
                print(f"Aviso: O arquivo '{nome_arquivo}' ignorado.") 
                continue # Continua para o próximo arquivo na lista

        if not arquivos_filtrados: 
            print("Nenhum arquivo encontrado.") # Imprime uma mensagem indicando que nenhum arquivo foi encontrado
            return False 

        colunas_id = [
            'CNPJ', 'Código Nacional', 'Município', 'UF', 'Modalidade de Cobrança', 
            'Tecnologia', 'Tecnologia Geração', 'Empresa', 'Porte da Prestadora', 
            'Tipo de Pessoa', 'Tipo de Produto', 'Código IBGE Município', 'Grupo Econômico'
        ] # Lista de colunas
        lazy_frames = [] 

        for arquivo in arquivos_filtrados: 
            lf = pl.scan_parquet(arquivo)
            lf = lf.filter(pl.col('Tipo de Produto') == 'M2M') # Filtra os dados para incluir apenas os registros onde a coluna 'Tipo de Produto' é igual a 'M2M'
            

            colunas_arquivo = lf.collect_schema().names()
            colunas_periodo = [col for col in colunas_arquivo if col not in colunas_id]
            colunas_id_presentes = [col for col in colunas_id if col in colunas_arquivo]

            # unpivot
            lf = lf.unpivot(
                index=colunas_id_presentes,
                on=colunas_periodo,
                variable_name='periodo',
                value_name='acessos'
            )
            
            # Limpeza e transformação de tipos
            lf = lf.with_columns([
                # Converte string para data (adiciona '-01' no final se o formato for apenas YYYY-MM para o Polars aceitar como data válida)
                (pl.col('periodo') + '-01').str.to_date(format='%Y-%m-%d', strict=False).alias('data_periodo'),
                pl.col('acessos').fill_null(0).cast(pl.Int32),
                pl.col('CNPJ').cast(pl.String).str.zfill(14)
            ])
            
            # Extrai ano e mês
            lf = lf.with_columns([
                pl.col('data_periodo').dt.year().alias('ano'),
                pl.col('data_periodo').dt.month().alias('mes')
            ]).drop('data_periodo')

            lazy_frames.append(lf)

        lf_final = pl.concat(lazy_frames, how="vertical")

        
        caminho_saida = os.path.join(DIR_DATAPROCESSED, 'preprocessado.parquet')

        lf_final.sink_parquet(caminho_saida)
        
        print(f"Compilação concluída. Arquivo salvo em: {caminho_saida}")
        return True

    except Exception as e:
        print(f"Erro ao compilar com Polars: {e}")
        return False
    

if __name__ == "__main__":
    compile_parquet() # Chama a função de compilação dos arquivos
