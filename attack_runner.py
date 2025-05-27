# attack_runner.py
import importlib
import time
from config.config import ATTACK_SCRIPTS, TARGET_INFO
from config.logging_config import setup_logging

def run_all_attacks():
    """
    Executa todos os ataques definidos em ATTACK_SCRIPTS.
    Retorna uma lista de dicts: {
      'attack': module_name,
      'status': status_str,
      'execution_time': float_seconds,
      'output': raw_output_or_exception
    }
    """
    setup_logging()
    import logging
    logger = logging.getLogger(__name__)

    results = []
    for attack in ATTACK_SCRIPTS:
        module_name = attack['module']
        # monta params
        params = {k: TARGET_INFO[v] for k, v in attack['params'].items()}
        logger.info(f"▶️  Iniciando ataque {module_name} com {params}")
        start = time.time()
        try:
            module = importlib.import_module(f'attack_scripts.{module_name}')
            raw = module.run_attack(params)
            status = 'Sucesso' if 'Sucesso' in str(raw) or 'Success' in str(raw) else 'Falha'
        except Exception as e:
            raw = str(e)
            status = 'Erro'
        duration = round(time.time() - start, 2)
        logger.info(f"⏹  {module_name} terminou em {duration}s com status {status}")
        results.append({
            'attack': module_name,
            'status': status,
            'execution_time': duration,
            'output': raw
        })
    return results
