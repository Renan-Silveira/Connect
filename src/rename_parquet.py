def rename_parquet():
    import pyarrow.csv as pv # Biblioteca para ler arquivos CSV e convertê-los em tabelas Parquet usando PyArrow
    import pyarrow.parquet as pq # Biblioteca para escrever tabelas Parquet usando PyArrow
    from pathlib import Path # Biblioteca para manipulação de caminhos de arquivos, facilita a construção de caminhos de forma portátil
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    DIR_DATARAW = os.getenv("DIR_DATARAW") # Obtém o diretório onde os dados extraídos serão salvos a partir das variáveis de ambiente
    DIR_DATAPARQUET = os.getenv("DIR_DATAPARQUET") # Obtém o diretório onde os arquivos Parquet serão salvos a partir das variáveis de ambiente
    try:

        Path(DIR_DATAPARQUET).mkdir(parents=True, exist_ok=True) # Garante que o diretório para os arquivos Parquet exista, criando-o se necessário

        def renomear_arquivo_parquet(nome_antigo): # Função para renomear o arquivo CSV para o formato Parquet, mantendo o nome base e mudando a extensão
            nome_sem_extensao = Path(nome_antigo).stem  # Obtém o nome do arquivo sem a extensão usando pathlib
            novo_nome = f"{nome_sem_extensao}.parquet"  # Cria o novo nome com a extensão .parquet
            return novo_nome  # Retorna o novo nome do arquivo

        for arquivo in os.listdir(DIR_DATARAW): # Itera sobre os arquivos no diretório de dados brutos
            if arquivo.endswith('.csv'):  # Verifica se o arquivo tem a extensão .csv
                caminho_completo = os.path.join(DIR_DATARAW, arquivo)  # Constrói o caminho completo para o arquivo CSV usando os.path.join para garantir portabilidade entre sistemas operacionais
                
                parse_options = pv.ParseOptions(delimiter=';')
                df = pv.read_csv(caminho_completo, parse_options=parse_options) # Lê o arquivo CSV usando PyArrow
                
                novo_nome = renomear_arquivo_parquet(arquivo) # Define o novo nome e caminho
                caminho_destino = os.path.join(DIR_DATAPARQUET, novo_nome) # Constrói o caminho completo para o arquivo Parquet usando os.path.join para garantir portabilidade entre sistemas operacionais
                
                pq.write_table(df, caminho_destino, compression='snappy') # Salva o DataFrame em formato Parquet com compressão Snappy
                
                os.remove(caminho_completo) # Remove o arquivo CSV original para economizar espaço em disco
                
                print(f"Convertido: {arquivo} -> {novo_nome}") # Imprime uma mensagem indicando que o arquivo foi convertido e renomeado
        return True # Retorna True para indicar que a renomeação foi concluída com sucesso
    except Exception as e: # Captura qualquer exceção que possa ocorrer durante a renomeação dos arquivos
        print(f"Erro ao renomear arquivos: {e}") # Imprime uma mensagem de erro caso ocorra um problema durante a renomeação dos arquivos
        return False # Retorna False para indicar que a renomeação falhou
if __name__ == "__main__":
    rename_parquet()