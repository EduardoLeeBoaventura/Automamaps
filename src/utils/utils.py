import os
import pandas as pd
import logging
from datetime import datetime
from src.config import settings

def get_timestamp():
    """Retorna um timestamp formatado para nomes de arquivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def create_directories():
    """Cria os diretórios de input, output e logs se não existirem."""
    logging.info("Verificando estrutura de pastas...")
    os.makedirs(settings.INPUT_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)

def get_input_files():
    """Retorna uma lista de todos os arquivos .xlsx na pasta de input."""
    files = [
        os.path.join(settings.INPUT_DIR, f)
        for f in os.listdir(settings.INPUT_DIR)
        if f.endswith(".xlsx") and not f.startswith("~")
    ]
    if not files:
        logging.warning(f"Nenhum arquivo .xlsx encontrado em '{settings.INPUT_DIR}'")
    else:
        logging.info(f"Arquivos .xlsx encontrados: {len(files)}")
    return files

def read_excel_column(file_path):
    """
    Lê uma coluna específica de um arquivo Excel.
    Retorna uma lista de nomes (strings).
    """
    column_name = settings.EXCEL_COLUMN_NAME
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        if column_name in df.columns:
            # Converte tudo para string e remove valores nulos/NaN
            names = df[column_name].dropna().astype(str).tolist()
            logging.info(f"Lidos {len(names)} nomes do arquivo: {file_path}")
            return names
        else:
            logging.error(f"Coluna '{column_name}' não encontrada em {file_path}")
            return []
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo {file_path}: {e}")
        return []

def write_output_file(output_path, content):
    """Escreve o conteúdo final no arquivo de texto de saída."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Arquivo de resultado salvo com sucesso em: {output_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo de saída: {e}")