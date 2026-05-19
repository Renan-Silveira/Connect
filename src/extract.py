def extract():
    import requests # Biblioteca para fazer requisições HTTP
    import os # Biblioteca para interagir com o sistema operacional
    from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

    load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

    URL = os.getenv("URL") # Obtém a URL do arquivo a ser baixado a partir das variáveis de ambiente
    DIR_DATA = os.getenv("DIR_DATA") # Obtém o diretório onde o arquivo será salvo a partir das variáveis de ambiente
    with requests.get(URL, stream=True) as response:
        response.raise_for_status()

        with open(f"{DIR_DATA}/download.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    print("Download concluído.")


if __name__ == "__main__":
    extract()
