# FAIR: Ambiente e Testes de Segurança Abertos e Automatizados em Redes SDN


[![Licença](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)

## Resumo:

_Este artigo apresenta a FAIR, uma ferramenta open source que simplifica testes de segurança em redes SDN. Sem a necessidade de configurações manuais extensas, a FAIR monta automaticamente um ambiente de rede de testes e executa simulações de ataques para demonstrar como uma rede SDN reage. O usuário pode personalizar cenários e coletar métricas sem intervenção constante. A FAIR foi validada em uma máquina virtual básica — onde todo o ambiente SDN foi construído do zero — e seu módulo de testes de segurança em um testbed da RNP. A FAIR mostrou-se fácil de usar, bem integrada às ferramentas comuns e capaz de fornecer resultados consistentes para suportar fluxos de desenvolvimento contínuo._

---

## Funcionalidades

- Automação Completa do Ambiente SDN:
  - instalação de Docker, Mininet e controladores (ONOS/Ryu), com detecção de sistema operacional e pull condicional de imagens.

- Topologia Virtual Inteligente:
  - criação e execução automática de topologias Mininet (padrão ou customizadas), com espera ativa pela conexão OpenFlow.

- Execução Automatizada de Ataques:
  - suporte a ataques como MAC Flood e SYN Flood.

- Arquitetura Modular:
  - novos scripts de ataque podem ser adicionados sem alterar a lógica principal do sistema.

- Coleta de Métricas:
  - tempo de execução, status de ataque, saída de ferramentas.

- Geração de Logs e Captura de Tráfego:
  - registros detalhados em .log.

- Parametrização Flexível:
  - configurações centralizadas em config.py, facilitando integração com pipelines DevOps e CI/CD.

---

## Pré-requisitos

- Acesso root ou usuário com permissão de sudo
- Conexão à Internet para baixar pacotes e imagens Docker
- Hardware mínimo: 4 GB de RAM, 2 vCPUs, 10 GB de espaço em disco livre

- Ferramentas externas:
  - `macof`
  - `hping3`

- Testado com:

  - Kali Linux/Ubuntu
  - Mininet
  - Controlador ONOS/RYU

---

## Instalação e Uso

1. **Clone o repositório**

   ```bash
    git clone https://github.com/ryan-leal/FAIR-SBSeg25.git
    cd FAIR-SBSeg25
   ```

2. **Configurar os ataques em config/config.py**

```python
ATTACK_SCRIPTS = [
    {'module': 'macof_attack', 'params': {'interface': 'INTERFACE'}},
    {'module': 'hping_attack', 'params': {'target': 'IP', 'interface': 'INTERFACE'}}
    # Adicione mais ataques conforme necessário
    # Padrao:
    # {'module': 'nome_Ataque', 'params': {'param1': 'REFValor', 'param2': 'REFValor2'}}
]

# Informações sobre o alvo
# Deve ter o mesmo nome do REFValor acima e segue o padrao:
# 'REFValor1': 'valorReal', ...
TARGET_INFO = {
    'IP': '10.0.0.2',
    'INTERFACE': 'h1-eth0',
    'MAX_TIME': '30'
}
```

3. **Execute o script**

   ```bash
   sudo python orchestrator.py
   ```
   - Na primeira execução, se o Docker não estiver instalado, você será instruído a fazer **logout/login** após a instalação para aplicar o grupo `docker`. Depois, execute novamente (Em caso de erro recorrente, reinicie a máquina).
   - Todas as etapas (instalação de pacotes, pull de imagens, criação de containers, topo Mininet) são automatizadas.
  
4. **Escolha do Controlador**
   Ao final das dependências, o script exibirá:

   ```
   Escolha o controlador SDN:
   1) ONOS
   2) Ryu
   ```

   Digite `1` para ONOS ou `2` para Ryu e pressione **Enter**. O controlador será iniciado e, em seguida, o Mininet conectará um topo em árvore automaticamente.
---

## Estrutura da Ferramenta

```
FAIR-SBSeg25-main/
├── attack_scripts/
│   ├── hping_attack.py
│   └── macof_attack.py
├── config/
│   ├── config.py
│   ├── logging_config.py
│   └── result_logger.py
├── results/
├── README.md 
├── fair.py
├── metrics.py
├── mininetTopo.py
├── orchestrator.py
├── provision_env.sh

```

---


## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
