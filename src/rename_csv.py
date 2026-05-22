def rename_csv():
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    DIR_DATARAW = os.getenv("DIR_DATARAW") # Obtém o diretório onde os dados extraídos serão salvos a partir das variáveis de ambiente
    try:
        for nome_arquivo in os.listdir(DIR_DATARAW):
            if nome_arquivo.endswith(".csv"):
                # Divide o nome pelo underscore
                partes = nome_arquivo.split('_')
                
                # Verifica se o arquivo tem pelo menos 3 underscores
                if len(partes) > 3:
                    # Junta as partes a partir da 3ª posição (índice 3)
                    # Se quiser manter o 3º, mude para partes[2:]
                    novo_nome = "_".join(partes[3:])
                    
                    # Renomeia o arquivo
                    os.rename(os.path.join(DIR_DATARAW, nome_arquivo), os.path.join(DIR_DATARAW, novo_nome))
                    print(f"Renomeado: {nome_arquivo} -> {novo_nome}")
                else:
                    print(f"Pulado (menos de 3 underscores): {nome_arquivo}")
        return True # Retorna True para indicar que a renomeação foi concluída com sucesso
    except Exception as e: # Captura qualquer exceção que possa ocorrer durante a renomeação dos arquivos
        print(f"Erro ao renomear arquivos: {e}") # Imprime uma mensagem de erro caso ocorra um problema durante a renomeação dos arquivos
        return False # Retorna False para indicar que a renomeação falhou
if __name__ == "__main__":
    rename_csv()