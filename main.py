import importlib # Auxiliar no controle dos modulos
import logging # Responsavel pelos logs
import time # Calcular metricas de tempo
from config.config import ATTACK_SCRIPTS, TARGET_INFO
from config.logging_config import setup_logging
from config.result_logger import log_result, display_results

def main():
    setup_logging() # inicia a ferramenta de logs
    logger = logging.getLogger(__name__)
    total_start_time = time.time() # CRONOMETRO DE FERRAMENTA INICIADO
    
    # Para cada modulo adicionado em ATTACK_SCRIPTS (config/config.py)
    for attack in ATTACK_SCRIPTS:
        # Extrai o nome do modulo dessa iteracao
        module_name = attack['module'] 

        # Extracao de informacoes dos parametros a partir de 'params' e 'TARGET_INFO' (config/config.py)
        # key: Valor eh extraido de params, contendo o nome do parametro
        # value: REFValor de 'ATTACK_SCRIPTS->params' que sera usado como chave para o valor verdadeiro
        # TARGET_INFO[value]: extrai o valor do parametro a partir de TARGET_INFO e usando o 'value'
        params = {key: TARGET_INFO[value] for key, value in attack['params'].items()}
        
        try:
            logger.info(f"Executando ataque: {module_name} com parâmetros: {params}")

            attack_start_time = time.time() # CRONOMETRO DE ATAQUE INICIADO
            
            # Busca o script da iteracao na pasta de attack_scripts
            module = importlib.import_module(f'attack_scripts.{module_name}')
            # result recebera o valor de retorno do script executado com os parametros da vez
            result = module.run_attack(params)

            attack_end_time = time.time() # CRONOMETRO DE ATAQUE ENCERRADO
            
            logger.info(f"Ataque {module_name} concluído com sucesso em {attack_end_time - attack_start_time:.2f} segundos")
            log_result(module_name, result) # Executa a funcao de log do resultado de script
        except KeyError as e:
            # Caso algum parametro esteja faltando em TARGET_INFO
            logger.error(f"Faltam informações do alvo de {module_name}: {e}", exc_info=True)
            result = f"Erro: Faltam informações do alvo de {module_name}: {e}"
            log_result(module_name, result)
        except Exception as e:
            # Captura outros casos de erro durante a execucao
            logger.error(f"Erro ao executar {module_name}: {e}", exc_info=True)
            result = f"Erro ao executar {module_name}: {e}"
            log_result(module_name, result)
    
    total_end_time = time.time() # CRONOMETRO DE FERRAMENTA ENCERRADO
    logger.info(f"Todos os ataques concluídos em {total_end_time - total_start_time:.2f} segundos")
    display_results()

if __name__ == "__main__":
    main()
