#!/usr/bin/env python3
"""
orchestrator.py: Integra provisionamento de ambiente (via script Bash) com execução de ataques e coleta de métricas.
"""

import subprocess
import os
import time
import click

# Caminhos para os scripts de provisionamento e topologia Mininet
PROVISION_SCRIPT = os.path.join(os.path.dirname(__file__), 'provision_env.sh')
MININET_SCRIPT = os.path.join(os.path.dirname(__file__), 'mininetTopo.py')

def run_provision(no_mininet=False):
    """
    Executa o script de provisionamento exibindo a saída linha por linha.
    Interrompe se for detectado pedido de relogin (por exemplo, após instalação do Docker).

    """
    cmd = [PROVISION_SCRIPT]
    if no_mininet:
        cmd.append('--no-mininet')  # Opcionalmente pula execução do Mininet no provisionamento
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in proc.stdout:
        click.echo(line.rstrip())  # Exibe saída em tempo real
        if "Faça LOGIN novamente" in line:
            proc.kill()            # Encerra execução se relogin for necessário
            return 1
    return proc.wait()             # Aguarda término do script e retorna o código de saída


@click.command()
@click.option('--skip-provision', is_flag=True, default=False,
              help='Pular provisionamento e assumir ambiente já levantado.')
@click.option('--report', default='report.json',
              help='Arquivo de saída JSON com resultados e métricas.')
def main(skip_provision, report):
    # Provisionamento do ambiente
    if not skip_provision:
        if not os.path.exists(PROVISION_SCRIPT):
            click.echo(click.style(f"❌ Script de provisionamento não encontrado: {PROVISION_SCRIPT}", fg='red'))
            return
        
        click.echo("🔧 Executando provisionamento do ambiente...")
        subprocess.run(['chmod', '+x', PROVISION_SCRIPT], check=True)  # Garante permissão de execução
        
        code = run_provision(no_mininet=True)
        
        if code == 1:
            # Caso seja necessário relogar após instalação do Docker
            click.secho(
                "\n⚠️  Docker foi instalado, mas você precisa relogar no sistema "
                "para aplicar as permissões. Depois disso, execute novamente:\n\n"
                "  sudo python3 orchestrator.py\n",
                fg='yellow'
            )
            return
        elif code != 0:
            click.secho(f"\n❌ Provisionamento falhou com código {code}.", fg='red')
            return
        
        click.echo("✅ Ambiente provisionado. Aguardando estabilização (10s)...")
        time.sleep(10)

    # Execução do script Mininet
    mnproc = subprocess.Popen(
        ['python', '-u', MININET_SCRIPT],  # Executa com saída não-bufferizada (-u)
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Lê e exibe a saída do Mininet linha por linha 
    try:
        while True:
            line = mnproc.stdout.readline()
            if not line:
                if mnproc.poll() is not None:
                    break  # Processo terminou
                continue    # Ainda sem saída, continua aguardando
            click.echo(f"[mn] {line.strip()}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if mnproc.poll() is None:
            mnproc.terminate()  # Finaliza processo se ainda estiver rodando

if __name__ == '__main__':
    main()
