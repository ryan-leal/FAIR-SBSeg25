#!/usr/bin/env python3
"""
orchestrator.py: Integra provisionamento de ambiente (via script Bash) com execução de ataques e coleta de métricas.
"""
import subprocess
import os
import time
import json
import click

from attack_runner import run_all_attacks
import metrics

PROVISION_SCRIPT = os.path.join(os.path.dirname(__file__), 'provision_env.sh')

def run_provision(no_cli=False):
    """Executa provision_env.sh linha a linha, para mostrar logs e capturar o prompt de relogin."""
    cmd = [PROVISION_SCRIPT]
    if no_cli:
    	cmd.append('--no-cli')
    
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
        code = run_provision(no_cli=True)
        if code == 1:  # relogin
            click.secho(
                "\n⚠️  Docker foi instalado, mas você precisa relogar no sistema "
                "para aplicar as permissões. Depois disso, execute again:\n\n"
                "  python3 orchestrator.py --skip-provision\n",
                fg='yellow'
            )
            return
        elif code != 0:
            click.secho(f"\n❌ Provisionamento falhou com código {code}.", fg='red')
            return
        click.echo("✅ Ambiente provisionado. Aguardando estabilização (10s)...")
        time.sleep(10)

    # 2) Métricas antes dos ataques
    click.echo("📊 Coletando métricas iniciais...")
    m_before = metrics.snapshot_container_stats('onos-controller')
    click.echo(f"   CPU_before={m_before['CPU']}%, Mem_before={m_before['MemUsage']}")

    # 3) Executar todos os ataques
    click.echo("🚀 Executando suíte de ataques...")
    results = run_all_attacks()
    click.echo(f"✅ Ataques concluídos: {len(results)} módulos executados.")

    # 4) Métricas após ataques
    click.echo("📊 Coletando métricas finais...")
    m_after = metrics.snapshot_container_stats('onos-controller')
    click.echo(f"   CPU_after={m_after['CPU']}%, Mem_after={m_after['MemUsage']}")

    # 5) Latência de rede (ping)
    target_ip = metrics.get_target_ip()
    click.echo(f"🌐 Medindo latência para {target_ip}...")
    latency = metrics.measure_latency(target_ip)
    click.echo(f"   Latência média: {latency} ms")

    # 6) Gerar relatório JSON
    report_data = {
        'metrics_before': m_before,
        'attack_results': results,
        'metrics_after': m_after,
        'latency_ms': latency
    }
    with open(report, 'w') as f:
        json.dump(report_data, f, indent=2)
    click.echo(click.style(f"📁 Relatório gerado: {report}", fg='green'))

if __name__ == '__main__':
    main()
