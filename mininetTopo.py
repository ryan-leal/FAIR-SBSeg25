#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import subprocess

def run():
    # =====================
    # 1. Configuration Setup
    # =====================
    CONTROLLER_IP = '127.0.0.1'  # Localhost
    OF_PORT = 6633               # ONOS default port
    TOPO_DEPTH = 2
    TOPO_FANOUT = 2
    
    # =====================
    # 2. Topology Setup
    # =====================
    info('*** Creating tree topology: depth={}, fanout={}\n'.format(TOPO_DEPTH, TOPO_FANOUT))
    topo = TreeTopo(depth=TOPO_DEPTH, fanout=TOPO_FANOUT)
    
    # =====================
    # 3. Controller Setup
    # =====================
    info('*** Configuring remote controller: {}:{}\n'.format(CONTROLLER_IP, OF_PORT))
    controller = RemoteController(
        'c0', 
        ip=CONTROLLER_IP, 
        port=OF_PORT,
        protocols='OpenFlow13'  # Explicit protocol specification
    )
    
    # =====================
    # 4. Network Initialization
    # =====================
    info('*** Creating Mininet network\n')
    net = Mininet(
        topo=topo,
        controller=controller,
        switch=OVSSwitch,        # ovsk = OVS kernel switch
        autoSetMacs=True,        # Automatically set MAC addresses
        waitConnected=True      # Wait for switches to connect
    )
    
    # =====================
    # 5. Start Network
    # =====================
    net.start()
    
    # =====================
    # 6. Additional Configuration
    # =====================
    # Explicitly set OpenFlow version on each switch
    for switch in net.switches:
        info('*** Configuring switch {} to use OpenFlow13\n'.format(switch.name))
        switch.cmd('ovs-vsctl set bridge', switch, 'protocols=OpenFlow13')
    
    info('*** Waiting switches initializing...\n')
    time.sleep(10)
    # =====================
    # 7. Test Connectivity
    # =====================
    info('*** Testing network connectivity\n')
    net.pingAll()
    
    # =====================
    # 8. Start CLI (Interactive Mode)
    # =====================
    h1 = net.get('h1')
    
    proc = h1.popen(
        ['python', '-u', 'fair.py'],  # -u is CRITICAL here
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Read output line by line in real-time
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break  # Process finished
                continue  # No output yet
            print(f"[h1] {line.strip()}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if proc.poll() is None:
            proc.terminate()
    
    
    # =====================
    # 9. Cleanup
    # =====================
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')  # Set log level to show info messages
    run()
