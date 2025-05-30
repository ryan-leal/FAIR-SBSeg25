#!/usr/bin/env python3
"""
orchestrator.py: Integra provisionamento de ambiente (via script Bash) com execução de ataques e coleta de métricas.
"""
import subprocess
import os
import time
import click

PROVISION_SCRIPT = os.path.join(os.path.dirname(__file__), 'provision_env.sh')
MININET_SCRIPT = os.path.join(os.path.dirname(__file__), 'mininetTopo.py')

def run_provision(no_mininet=False):
    """Executa provision_env.sh linha a linha, para mostrar logs e capturar o prompt de relogin."""
    cmd = [PROVISION_SCRIPT]
    if no_mininet:
    	cmd.append('--no-mininet')
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        click.echo(line.rstrip())              # mostre tudo
        if "Faça LOGIN novamente" in line:
            proc.kill()                        # interrompe o script
            return 1                           # sinaliza relogin necessário
    return proc.wait()


@click.command()
@click.option('--skip-provision', is_flag=True, default=False,
              help='Pular provisionamento e assumir ambiente já levantado.')
@click.option('--report', default='report.json',
              help='Arquivo de saída JSON com resultados e métricas.')
def main(skip_provision, report):
    # 1) Provisionamento
    if not skip_provision:
        if not os.path.exists(PROVISION_SCRIPT):
            click.echo(click.style(f"❌ Script de provisionamento não encontrado: {PROVISION_SCRIPT}", fg='red'))
            return
        click.echo("🔧 Executando provisionamento do ambiente...")
        subprocess.run(['chmod', '+x', PROVISION_SCRIPT], check=True)
        # Executar e capturar saída
        code = run_provision(no_mininet=True)
        if code == 1:  # relogin
            click.secho(
                "\n⚠️  Docker foi instalado, mas você precisa relogar no sistema "
                "para aplicar as permissões. Depois disso, execute novamente:\n\n"
                "  python3 orchestrator.py --skip-provision\n",
                fg='yellow'
            )
            return
        elif code != 0:
            click.secho(f"\n❌ Provisionamento falhou com código {code}.", fg='red')
            return
        click.echo("✅ Ambiente provisionado. Aguardando estabilização (10s)...")
        time.sleep(10)
        
    mnproc = subprocess.Popen(
        ['python', '-u', MININET_SCRIPT], 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Read output line by line in real-time
    try:
        while True:
            line = mnproc.stdout.readline()
            if not line:
                if mnproc.poll() is not None:
                    break  # Process finished
                continue  # No output yet
            click.echo(f"[mn] {line.strip()}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if mnproc.poll() is None:
            mnproc.terminate()


if __name__ == '__main__':
    main()
