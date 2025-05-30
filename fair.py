import importlib # Auxiliar no controle dos modulos
import logging # Responsavel pelos logs
import time # Calcular metricas de tempo
import click
import subprocess
import json

from config.config import ATTACK_SCRIPTS, TARGET_INFO
from config.logging_config import setup_logging
from config.result_logger import log_result, display_results
import metrics

def detect_running_controller():
    out = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True)
    if 'onos-controller' in out:
        return 'onos-controller'
    elif 'ryu-controller' in out:
        return 'ryu-controller'
    else:
        raise RuntimeError("Nenhum controlador ativo foi detectado.")


def main():
    setup_logging() # inicia a ferramenta de logs
    logger = logging.getLogger(__name__)
    total_start_time = time.time() # CRONOMETRO DE FERRAMENTA INICIADO
    
    # Utilizados para coletar metricas
    controller_name = detect_running_controller()
    target_ip = metrics.get_target_ip()
    
    # Para cada modulo adicionado em ATTACK_SCRIPTS (config/config.py)
    results = []
    metricsData = []
    for attack in ATTACK_SCRIPTS:
        # Extrai o nome do modulo dessa iteracao
        module_name = attack['module'] 

        # Extracao de informacoes dos parametros a partir de 'params' e 'TARGET_INFO' (config/config.py)
        # key: Valor eh extraido de params, contendo o nome do parametro
        # value: REFValor de 'ATTACK_SCRIPTS->params' que sera usado como chave para o valor verdadeiro
        # TARGET_INFO[value]: extrai o valor do parametro a partir de TARGET_INFO e usando o 'value'
        params = {key: TARGET_INFO[value] for key, value in attack['params'].items()}
        
        try:
            # 1) Métricas antes do ataque
            click.echo("📊 Coletando métricas iniciais...")
            m_before = metrics.snapshot_container_stats(controller_name)
            click.echo(f"   CPU_before={m_before['CPU']}%, Mem_before={m_before['MemUsage']}")
            
            # 2) Latência de rede (ping) antes do ataque
            click.echo(f"🌐 Medindo latência para {target_ip}...")
            latency_before = metrics.measure_latency(target_ip)
            click.echo(f"   Latência média antes do ataque: {latency_before} ms")
            
            # 3) Execucao do ataque
            
            logger.info(f"Executando ataque: {module_name} com parâmetros: {params}")

            attack_start_time = time.time() # CRONOMETRO DE ATAQUE INICIADO
            
            # Busca o script da iteracao na pasta de attack_scripts
            module = importlib.import_module(f'attack_scripts.{module_name}')
            # result recebera o valor de retorno do script executado com os parametros da vez
            result = module.run_attack(params)
            
            attack_end_time = time.time() # CRONOMETRO DE ATAQUE ENCERRADO
            
            
            # 4) Métricas após ataque
            click.echo("📊 Coletando métricas finais...")
            m_after = metrics.snapshot_container_stats(controller_name)
            click.echo(f"   CPU_after={m_after['CPU']}%, Mem_after={m_after['MemUsage']}")
            
            # 5) Latência de rede (ping) apos ataque
            click.echo(f"🌐 Medindo latência para {target_ip}...")
            latency_after = metrics.measure_latency(target_ip)
            click.echo(f"   Latência média depois do ataque: {latency_after} ms")
            
            status = 'Sucesso' if 'Sucesso' in str(result) or 'Success' in str(result) else 'Falha'  # Define sucesso ou nao do ataque
            duration = round(attack_end_time - attack_start_time, 2) # calculo de duracao do ataque
            logger.info(f"Ataque {module_name} concluído com status {status} em {duration} segundos")
            log_result(module_name, result) # Executa a funcao de log do resultado de script
            
            metricsData.append({
                'usage_before': m_before,
                'latency_before': latency_before,
                'usage_after': m_after,
                'latency_after': latency_after
            })
            results.append({
                'attack': module_name,
                'status': status,
                'execution_time': duration,
                'metrics': metricsData,
                'output': result
                
            })
            
            metricsData = []
            logger.info(f"Aguardando 30s para estabilizar o ambiente...")
            time.sleep(30)
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
    
    # 6) Gerar relatório JSON
    report_data = {
        'attack_results': results
    }
    report = 'report.json'
    with open(report, 'w') as f:
        json.dump(report_data, f, indent=2)
    click.echo(click.style(f"📁 Relatório gerado: {report}", fg='green'))

if __name__ == "__main__":
    main()
