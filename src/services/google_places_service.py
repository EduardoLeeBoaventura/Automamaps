import requests
import logging
import time
from config import settings

def find_place_location(search_text):
    """
    Etapa 1: Encontra a localização (lat, long) de um nome de condomínio.
    Usa a API "Find Place".
    """
    
    # Adicionamos o filtro de localidade diretamente na string de busca.
    filtered_search_text = f"{search_text}, Aracaju, Sergipe"
    logging.info(f"Aplicando filtro de local. Buscando por: '{filtered_search_text}'")

    params = {
        'input': filtered_search_text, 
        'inputtype': 'textquery',
        'fields': 'geometry/location,name,place_id',
        'key': settings.API_KEY
    }
    
    try:
        response = requests.get(settings.BASE_URL_FIND_PLACE, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'OK':
            candidate = data.get('candidates', [])[0] 
            location = candidate['geometry']['location']
            found_name = candidate['name']
            place_id = candidate['place_id']
            logging.info(f"Encontrado: '{search_text}' -> '{found_name}' (ID: {place_id})")
            return location['lat'], location['lng'], found_name, place_id
        else:
            logging.warning(f"API Find Place não encontrou '{search_text}' em Aracaju/SE. Status: {data.get('status')}")
            return None, None, None, None

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de conexão na API Find Place: {e}")
        return None, None, None, None
    except Exception as e:
        logging.error(f"Erro inesperado em find_place_location: {e}")
        return None, None, None, None


# --- FUNÇÃO ANTIGA (nearby_search) REMOVIDA ---
# --- NOVA FUNÇÃO ABAIXO ---

def text_search_for_keywords(lat, lng, radius, keywords):
    """
    Etapa 2 (NOVA): Busca por palavras-chave específicas usando "Text Search".
    Isso é feito para cada palavra-chave para evitar o filtro de "prominência".
    """
    all_results = []
    
    # Para cada palavra-chave, faremos uma busca completa
    for keyword in keywords:
        logging.info(f"Buscando pela palavra-chave: '{keyword}'...")
        
        params = {
            'query': keyword, # A palavra-chave se torna a query
            'location': f"{lat},{lng}",
            'radius': radius,
            'key': settings.API_KEY
        }
        
        try:
            while True:
                response = requests.get(settings.BASE_URL_TEXT_SEARCH, params=params)
                data = response.json()
                
                if response.status_code == 200:
                    results = data.get('results', [])
                    all_results.extend(results)
                    
                    next_page_token = data.get('next_page_token')
                    if next_page_token:
                        logging.info("Múltiplas páginas de resultados. Buscando próxima...")
                        time.sleep(2) 
                        params = {'pagetok': next_page_token, 'key': settings.API_KEY}
                    else:
                        break # Fim das páginas para esta palavra-chave
                else:
                    logging.error(f"Erro na API Text Search ({keyword}). Status: {data.get('status')}")
                    break # Erro, parar de buscar esta palavra-chave
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão na API Text Search ({keyword}): {e}")
            continue # Tenta a próxima palavra-chave
        except Exception as e:
            logging.error(f"Erro inesperado em text_search_for_keywords ({keyword}): {e}")
            continue # Tenta a próxima palavra-chave

    logging.info(f"Text Search encontrou {len(all_results)} resultados brutos (com duplicatas).")
    return all_results