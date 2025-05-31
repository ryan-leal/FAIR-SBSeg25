# metrics.py

import subprocess 
import re         
from config.config import TARGET_INFO 

def snapshot_container_stats(container):
    """
    Executa `docker stats --no-stream --format "{{.CPUPerc}};{{.MemUsage}}" container`
    e retorna um dicionário com as métricas de CPU e memória.

    Parâmetros:
        container (str): Nome ou ID do contêiner Docker.

    Retorno:
        dict: {'CPU': float (uso em %), 'MemUsage': str ('usado/total')}
    """

    # Define o formato de saída do comando para capturar apenas uso de CPU e memória
    fmt = '"{{.CPUPerc}};{{.MemUsage}}"'

    cmd = ['docker', 'stats', '--no-stream', '--format', fmt, container]

    # Executa o comando e captura a saída como texto, removendo espaços e aspas extras
    out = subprocess.check_output(cmd, text=True).strip().strip('"')

    # Separa a saída nas duas métricas: uso de CPU e uso de memória
    cpu_str, mem = out.split(';')

    # Converte o uso de CPU de string com '%' para float
    cpu = float(cpu_str.strip('%'))

    # Retorna um dicionário com os valores extraídos
    return {'CPU': cpu, 'MemUsage': mem}

def get_target_ip():
    """
    Retorna o IP do alvo a ser monitorado ou atacado.

    O IP é extraído do dicionário de configuração TARGET_INFO.

    Retorno:
        str: Endereço IP como string.
    """
    return TARGET_INFO.get('IP')  # Recupera o valor associado à chave 'IP'

def measure_latency(ip, count=5):
    """
    Mede a latência média de rede até o IP alvo usando o comando ping.

    Parâmetros:
        ip (str): Endereço IP de destino.
        count (int): Número de pacotes a serem enviados (padrão: 5).

    Retorno:
        float | None: Tempo médio de latência em milissegundos (ms),
                      ou None caso não seja possível extrair a média.
    """

    # Montamos o comando ping com a quantidade de pacotes especificada
    cmd = ['ping', '-c', str(count), ip]

    # Executamos o ping e captura a saída completa
    out = subprocess.check_output(cmd, text=True)

    # Usa expressão regular para localizar a linha com estatísticas de tempo 
    m = re.search(r'rtt [^=]+= ([\d\.]+)/([\d\.]+)/', out)

    if m:
        return float(m.group(2))
    else:
        return None
