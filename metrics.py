# metrics.py
import subprocess
import re
from config.config import TARGET_INFO

def snapshot_container_stats(container):
    """
    Executa `docker stats --no-stream --format "{{.CPUPerc}};{{.MemUsage}}" container`
    e retorna {'CPU': float, 'MemUsage': 'used/total'}.
    """
    fmt = '"{{.CPUPerc}};{{.MemUsage}}"'
    cmd = ['docker', 'stats', '--no-stream', '--format', fmt, container]
    out = subprocess.check_output(cmd, text=True).strip().strip('"')
    cpu_str, mem = out.split(';')
    cpu = float(cpu_str.strip('%'))
    return {'CPU': cpu, 'MemUsage': mem}

def get_target_ip():
    """Retorna o IP definido em TARGET_INFO."""
    return TARGET_INFO.get('IP')

def measure_latency(ip, count=5):
    """
    Executa `ping -c {count} {ip}` e retorna a média de tempo (ms).
    """
    cmd = ['ping', '-c', str(count), ip]
    out = subprocess.check_output(cmd, text=True)
    # procura a linha rtt min/avg/max/mdev = ...
    m = re.search(r'rtt [^=]+= ([\d\.]+)/([\d\.]+)/', out)
    if m:
        return float(m.group(2))
    else:
        return None
