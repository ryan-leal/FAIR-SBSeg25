import logging
# Saidas personalizadas para o resultado de um script e para mostrar os resultados.
logger = logging.getLogger(__name__)

def log_result(module_name, result):
    logger.info(f"Resultado do {module_name}: {result}")

def display_results():
    logger.info("Exibição dos resultados concluída. Verifique o arquivo result.log para detalhes.")
