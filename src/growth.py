def growth():
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
    from datetime import datetime, timedelta # Biblioteca para manipulação de datas e horas
    import pyarrow.dataset as ds # Biblioteca para manipular conjuntos de dados usando PyArrow

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env
    DIR_DATAPROCESSED = os.getenv("DIR_DATAPROCESSED") # Obtém o diretório onde o arquivo pré-processado será salvo a partir das variáveis de ambiente

    try:
        datacorte = datetime.today() - timedelta(days=365) # Define a data de corte como um dia antes da data atual
        datacorte = datacorte.strftime('%Y-%m-%d')
        df = ds.dataset(os.path.join(DIR_DATAPROCESSED, "preprocessado.parquet"), format="parquet")
        df_filtered = df.to_table(filter=ds.field('periodo') >= datacorte) # Filtra o DataFrame para incluir apenas os registros com período maior ou igual à data de corte
        df_filtered = df_filtered.to_pandas() # Converte o DataFrame filtrado para um DataFrame do Pandas para facilitar a manipulação e visualização
        print(df_filtered) # Imprime o DataFrame filtrado para verificação
        return True # Retorna True para indicar que a função foi executada com sucesso

    except Exception as e:
        print(f"Erro ao calcular a data de corte: {e}") # Imprime uma mensagem de erro caso ocorra uma exceção
        return False # Retorna False para indicar que a função falhou
if __name__ == "__main__":
    growth() # Chama a função growth para executar o código