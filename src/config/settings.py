import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega a chave de API do Google Places do arquivo .env
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# endpoints da API do Google Places
BASE_URL_FIND_PLACE = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
BASE_URL_NEARBY_SEARCH = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
BASE_URL_TEXT_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Diretórios padrão
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
LOG_DIR = "data/logs"

# Nome da coluna que o script vai procurar nos arquivos .xlsx
EXCEL_COLUMN_NAME = "Nome"

# Raio padrão em metros, caso o usuário não digite nada
DEFAULT_RADIUS = 500

# Palavras-chave para filtrar os resultados.
LOCAL_FILTER_KEYWORDS = [
    "condomínio",
    "residencial",
    "apartamento",
    "edifício",
    "conjunto",
    "complexo"
]

# Tipos de lugares que a API do Google vai focar.
# 'establishment' e 'point_of_interest' são tipos amplos que cobrem a maioria dos locais públicos.
SEARCH_TYPES = "establishment|point_of_interest"