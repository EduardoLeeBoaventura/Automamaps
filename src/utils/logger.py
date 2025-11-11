import logging
import os
import sys
from config import settings

def setup_logging(timestamp):
    log_filename = f"log_{timestamp}.log"
    log_filepath = os.path.join(settings.LOG_DIR, log_filename)

    # Formato da mensagem de log
    log_format = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - (%(filename)s:%(lineno)d) - %(message)s"
    )

    # Configura o logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Limpa handlers anteriores para evitar logs duplicados
    if logger.hasHandlers():
        logger.handlers.clear()

    # Salvar em arquivo
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # Mostrar no console (terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)
    
    logging.info(f"Logging configurado. Salvando em: {log_filepath}")
    return logger