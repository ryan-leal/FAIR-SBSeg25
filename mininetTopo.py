#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import subprocess

def run():
    # Configurações iniciais
    CONTROLLER_IP = '127.0.0.1'  # IP do controlador SDN
    OF_PORT = 6633               # Porta padrão do ONOS
    TOPO_DEPTH = 2               # Profundidade da topologia em árvore
    TOPO_FANOUT = 2              # Número de filhos por nó

    # Criação da topologia em árvore
    info('*** Creating tree topology: depth={}, fanout={}\n'.format(TOPO_DEPTH, TOPO_FANOUT))
    topo = TreeTopo(depth=TOPO_DEPTH, fanout=TOPO_FANOUT)

    # Definição do controlador remoto
    info('*** Configuring remote controller: {}:{}\n'.format(CONTROLLER_IP, OF_PORT))
    controller = RemoteController(
        'c0',
        ip=CONTROLLER_IP,
        port=OF_PORT,
        protocols='OpenFlow13'
    )

    # Inicialização da rede Mininet com o controlador e topologia
    info('*** Creating Mininet network\n')
    net = Mininet(
        topo=topo,
        controller=controller,
        switch=OVSSwitch,
        autoSetMacs=True,
        waitConnected=True
    )

    # Inicializa a rede
    net.start()

    # Configura manualmente o protocolo OpenFlow13 em cada switch
    for switch in net.switches:
        info('*** Configuring switch {} to use OpenFlow13\n'.format(switch.name))
        switch.cmd('ovs-vsctl set bridge', switch, 'protocols=OpenFlow13')

    # Aguarda switches estabilizarem
    info('*** Waiting switches initializing...\n')
    time.sleep(10)

    # Testa conectividade entre todos os hosts
    info('*** Testing network connectivity\n')
    net.pingAll()

    # Executa script 'fair.py' no host h1 e exibe saída em tempo real
    h1 = net.get('h1')
    proc = h1.popen(
        ['python', '-u', 'fair.py'],  # -u: modo unbuffered para saída em tempo real
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Exibe a saída do script linha por linha até que o processo termine ou seja interrompido
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            print(f"[h1] {line.strip()}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if proc.poll() is None:
            proc.terminate()

    # Finaliza a rede
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
