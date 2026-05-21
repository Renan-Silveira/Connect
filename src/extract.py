def extract():
    import requests # Biblioteca para fazer requisições HTTP
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
    import zipfile # Biblioteca para manipular arquivos ZIP
    from tqdm import tqdm
    import requests
    import logging
    from datetime import datetime

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    URL = os.getenv("URL") # Obtém a URL do arquivo a ser baixado a partir das variáveis de ambiente
    DIR_DATA = os.getenv("DIR_DATA") # Obtém o diretório onde o arquivo será salvo a partir das variáveis de ambiente
    DIR_DATARAW = os.getenv("DIR_DATARAW") # Obtém o diretório onde os dados extraídos serão salvos a partir das variáveis de ambiente
    NOME_FILE = os.getenv("NOME_FILE") # Obtém o nome do arquivo a ser salvo a partir das variáveis de ambiente

    # Configuração do log: salva em 'erros_download.txt', modo 'a' (append)
    logging.basicConfig(
        filename='erros_download.txt',
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    def download_file(URL, path): # Função para baixar um arquivo da URL especificada e salvar no caminho fornecido
        chunk_size = 1024 * 1024  # Aumenta o tamanho do chunk para 1MB (1024*1024) para reduzir chamadas de sistema
        
        try:
            with requests.get(URL, stream=True, timeout=(5, 30)) as response: # Faz uma requisição GET para a URL com streaming habilitado e timeout configurado
                response.raise_for_status() # Verifica se a requisição foi bem-sucedida, caso contrário, levanta uma exceção
                
                total_size = int(response.headers.get('content-length', 0)) # Obtém o tamanho total do arquivo a partir dos headers da resposta, ou 0 se não estiver disponível
                
                with open(path, "wb") as f:
                    # tqdm cria uma barra de progresso visual no terminal
                    with tqdm(total=total_size, unit='iB', unit_scale=True) as progress_bar:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk: # Filtra keep-alive chunks
                                f.write(chunk) # Escreve o chunk no arquivo
                                progress_bar.update(len(chunk)) # Atualiza a barra de progresso com o tamanho do chunk escrito
            print(f"\nDownload concluído com sucesso: {path}") # Imprime uma mensagem de sucesso após o download ser concluído
        
        except requests.exceptions.RequestException as e: # Captura erros relacionados a requisições HTTP
            print(f"\nErro ao baixar o arquivo: {e}") # Imprime uma mensagem de erro caso ocorra um problema durante o download
    try:
        #download_file(URL, f"{DIR_DATA}/{NOME_FILE}") # Chama a função para baixar o arquivo

        with zipfile.ZipFile(f"{DIR_DATA}/{NOME_FILE}", "r") as zip_ref: # Abre o arquivo ZIP para leitura
            zip_ref.extractall(DIR_DATARAW) # Extrai todo o conteúdo do arquivo ZIP para o diretório especificado

    except requests.exceptions.RequestException as e:
        # Registra o erro no arquivo .txt com o timestamp atual
        mensagem_erro = f"Falha ao baixar {URL}: {str(e)}"
        logging.error(mensagem_erro) # Registra o erro no arquivo de log
        print(f"Erro registrado. Verifique o arquivo erros_download.txt") # Imprime uma mensagem informando que o erro foi registrado
    except Exception as e: # Captura qualquer outra exceção que possa ocorrer durante a extração do arquivo
        print(f"\nErro ao extrair o arquivo: {e}") # Imprime uma mensagem de erro caso ocorra um problema durante a extração do arquivo

if __name__ == "__main__":
    extract()
