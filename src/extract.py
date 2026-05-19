def extract():
    import requests # Biblioteca para fazer requisições HTTP
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    URL = os.getenv("URL") # Obtém a URL do arquivo a ser baixado a partir das variáveis de ambiente
    DIR_DATA = os.getenv("DIR_DATA") # Obtém o diretório onde o arquivo será salvo a partir das variáveis de ambiente
    NOME_FILE = os.getenv("NOME_FILE") # Obtém o nome do arquivo a ser salvo a partir das variáveis de ambiente

    with requests.get(URL, stream=True) as response: # Faz uma requisição GET para a URL especificada, com streaming habilitado para baixar o arquivo em partes
        response.raise_for_status() # Verifica se a requisição foi bem-sucedida, lançando uma exceção se houve um erro

        with open(f"{DIR_DATA}/{NOME_FILE}", "wb") as f: # Abre um arquivo para escrita em modo binário no diretório especificado com o nome do arquivo
            for chunk in response.iter_content(chunk_size=8192): # Itera sobre o conteúdo da resposta em partes (chunks) de 8192 bytes
                f.write(chunk) # Escreve cada parte do conteúdo no arquivo aberto

if __name__ == "__main__":
    extract()
