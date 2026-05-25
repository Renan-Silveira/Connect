def main():
    from extract import extract
    from rename_parquet import rename_parquet
    from rename_csv import rename_csv
    from compile import compile_parquet
    from growth import growth
    import logging

    logging.basicConfig( # Configuração básica do logging para registrar informações no console
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    logger.info("Pipeline iniciada")

    steps = [ # Lista de etapas a serem executadas na pipeline
        extract,
        rename_csv,
        rename_parquet,
        compile_parquet,
        growth
    ]

    for step in steps:
        logger.info(f"Executando etapa: {step.__name__}") # Loga o início de cada etapa

        try:
            result = step() # Executa a etapa e captura o resultado

            if not result:
                logger.error(f"Etapa falhou: {step.__name__}") # Loga o erro e
                break

            logger.info(f"Etapa concluída: {step.__name__}") # Loga o sucesso da etapa

        except Exception as e:
            logger.exception(f"Erro inesperado em {step.__name__}: {e}") # Loga a exceção e
            break

    logger.info("Pipeline finalizada")
if __name__ == "__main__":
    main()