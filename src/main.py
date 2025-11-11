import logging
import os
import sys
from config import settings
from utils import utils, logger
from services import google_places_service

def get_user_radius():
    """Mostra o menu e pede o raio ao usuário."""
    print("--- 🗺️  Localizador de Condomínios Próximos ---")
    print(f"O raio padrão é de {settings.DEFAULT_RADIUS} metros.")
    
    radius_input = input("Deseja usar um raio diferente? (em metros) ou pressione [Enter] para o padrão: ")
    
    if not radius_input:
        radius = settings.DEFAULT_RADIUS
        print(f"Usando raio padrão: {radius}m")
    else:
        try:
            radius = int(radius_input)
            if radius <= 0:
                print("Valor inválido. Usando raio padrão.")
                radius = settings.DEFAULT_RADIUS
            else:
                print(f"Usando raio customizado: {radius}m")
        except ValueError:
            print("Entrada inválida. Usando raio padrão.")
            radius = settings.DEFAULT_RADIUS
    
    print("-" * 50)
    return radius

def process_condo_list(condo_names, radius, client_place_ids_set):
    """
    Processa uma lista de nomes, busca na API e formata a saída.
    Agora recebe o 'set' de IDs de clientes para filtragem.
    """
    output_content = []
    
    for condo_name in condo_names:
        if not condo_name or str(condo_name).strip() == "":
            continue
            
        logging.info(f"Processando cliente: '{condo_name}'")
        output_content.append(f"Cliente: {condo_name}")
        
        # Encontrar as coordenadas do condomínio principal
        lat, lng, found_name, main_place_id = google_places_service.find_place_location(condo_name)
        
        if lat is None:
            logging.warning(f"'{condo_name}' não encontrado no Google Maps.")
            output_content.append(" | NÃO ENCONTRADO NO MAPS\n---\n")
            continue

        # Buscar por lugares próximos usando as palavras-chave
        keywords_to_search = settings.LOCAL_FILTER_KEYWORDS
        nearby_places_raw = google_places_service.text_search_for_keywords(
            lat, lng, radius, keywords_to_search
        )
        
        if not nearby_places_raw:
            logging.info("Nenhum local próximo encontrado pela API.")
            output_content.append("\nCondomínios próximos:\n - Nenhum encontrado nos critérios.\n---\n")
            continue
            
        # Filtrar os resultados
        found_neighbors = set() 
        
        for place in nearby_places_raw:
            place_id = place.get('place_id')
            
            # --- FILTRO MODIFICADO (A SUA SOLICITAÇÃO) ---
            # Se o ID do local encontrado estiver na nossa lista de clientes,
            # pulamos ele. Não queremos listar nossos próprios clientes.
            if place_id in client_place_ids_set:
                continue 
            # --- FIM DA MODIFICAÇÃO ---

            place_name = place.get('name', '').lower()
                
            # Filtro final de palavras-chave para garantir
            if any(keyword in place_name for keyword in settings.LOCAL_FILTER_KEYWORDS):
                found_neighbors.add(place.get('name')) 
                
        # Etapa 4: Formatar a saída
        if not found_neighbors:
            output_content.append("\nCondomínios próximos:\n - Nenhum encontrado nos critérios.\n---\n")
        else:
            output_content.append("\nCondomínios próximos:\n")
            for neighbor in sorted(list(found_neighbors)):
                output_content.append(f" - {neighbor}\n")
            output_content.append("---\n")
            
    return "".join(output_content)


def main():
    # Configuração inicial
    timestamp = utils.get_timestamp()
    utils.create_directories()
    logger.setup_logging(timestamp) 
    
    logging.info("--- INÍCIO DA EXECUÇÃO ---")

    # Validação da Chave de API
    if not settings.API_KEY or settings.API_KEY == "SUA_CHAVE_API_AQUI":
        logging.error("="*50)
        logging.error("ERRO CRÍTICO: CHAVE DE API NÃO CONFIGURADA.")
        logging.error("Por favor, edite o arquivo .env e adicione sua GOOGLE_PLACES_API_KEY.")
        logging.error("="*50)
        print("Pressione [Enter] para sair.")
        input()
        sys.exit(1)

    # Mostra o menu e pegar o raio
    radius = get_user_radius()
    
    # Encontra arquivos .xlsx na pasta de input
    input_files = utils.get_input_files()
    if not input_files:
        logging.error(f"Nenhum arquivo .xlsx encontrado em '{settings.INPUT_DIR}'.")
        logging.error("Por favor, adicione seus arquivos e tente novamente.")
        print("Pressione [Enter] para sair.")
        input()
        sys.exit(1)
        
    all_names_to_process = []
    
    # lê todos os arquivos e juntar os nomes
    for file_path in input_files:
        logging.info(f"Lendo arquivo: {file_path}")
        names = utils.read_excel_column(file_path)
        all_names_to_process.extend(names)
        
    if not all_names_to_process:
        logging.error("Nenhum nome encontrado na coluna 'nome' dos arquivos.")
        print("Pressione [Enter] para sair.")
        input()
        sys.exit(1)
        
    logging.info(f"Total de {len(all_names_to_process)} condomínios para processar.")
    
    # Pre-processamento: encontrar IDs de todos os clientes
    print("Iniciando pré-processamento (Etapa 1 de 2)...")
    logging.info("Iniciando pré-processamento para encontrar IDs de todos os clientes...")
    
    client_place_ids_set = set()
    for name in all_names_to_process:
        if not name or str(name).strip() == "":
            continue
        # Usamos a mesma função 'find_place' para pegar o ID de cada cliente
        _, _, _, place_id = google_places_service.find_place_location(name)
        if place_id:
            client_place_ids_set.add(place_id)
        else:
            logging.warning(f"[Pré-processamento] Cliente '{name}' não encontrado no Maps. Será processado, mas não usado para filtro.")
            
    logging.info(f"Pré-processamento concluído. {len(client_place_ids_set)} IDs de clientes únicos foram encontrados e serão filtrados.")

    print("Iniciando processamento principal (Etapa 2 de 2)... Isso pode levar vários minutos.")
    
    # Processa a lista de nomes (agora passando o set de IDs)
    final_output_string = process_condo_list(all_names_to_process, radius, client_place_ids_set)

    # Salva o arquivo de resultado
    output_filename = f"resultado_{timestamp}.txt"
    output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
    utils.write_output_file(output_path, final_output_string)
    
    logging.info("--- FIM DA EXECUÇÃO ---")
    print("="*50)
    print("Processo concluído com sucesso!")
    print(f"Resultados salvos em: {output_path}")
    print(f"Logs salvos em: data/logs/log_{timestamp}.log")
    print("Pressione [Enter] para fechar.")
    input()

if __name__ == "__main__":
    main()