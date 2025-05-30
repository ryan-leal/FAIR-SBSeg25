#!/bin/bash

# Faz com que o script pare imediatamente se qualquer comando falhar (retornar código diferente de 0).
# Isso ajuda a evitar que o script continue em um estado inconsistente após um erro.
set -e

# Aceita um flag --no-cli para não abrir o CLI do Mininet
SKIP_MININET=0
if [ "$1" = "--no-mininet" ]; then
  SKIP_MININET=1
  echo "[INFO] Modo no-mininet: Ambiente sendo levantado sem o mininet."
fi

# Analise de Pre-requisitos:
echo "[INFO] Checando pre-requisitos..."

# 1) Detecta ID e codename do SO
OS_ID=$(grep ^ID= /etc/os-release | cut -d= -f2 | tr -d '"')
if [ "$OS_ID" = "kali" ]; then
  DOCKER_DIST="debian"                    # Kali usa repo Debian
  DOCKER_CODENAME="bookworm"              # Use 'bookworm' ou 'bullseye'
  export DEBIAN_FRONTEND=noninteractive
  export APT_LISTCHANGES_FRONTEND=none
else
  DOCKER_DIST="ubuntu"                    # Ubuntu usa próprio ID
  DOCKER_CODENAME=$(lsb_release -cs)      # ex: "focal", "jammy"
fi
echo "[INFO] Usando Docker repo: $DOCKER_DIST / $DOCKER_CODENAME"

# 2) Instala Docker CE se não existir
if ! command -v docker &> /dev/null; then
  echo "[INFO] Docker não encontrado. Instalando Docker CE..."
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl gnupg lsb-release

  sudo install -m0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/$DOCKER_DIST/gpg" \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg   # Baixa chave GPG oficial

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/$DOCKER_DIST \
    $DOCKER_CODENAME stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
                          docker-buildx-plugin docker-compose-plugin


    echo "[INFO] Adicionando usuário ao grupo Docker..."

    # Cria o grupo docker caso não exista
    sudo groupadd docker 2>/dev/null || true

    # Adiciona seu usuário ao grupo docker
    sudo usermod -aG docker $USER

    echo "[OK] Docker instalado com sucesso."
    echo "[INFO] Faça LOGIN novamente para salvar alteracoes de usuário docker e execute o script novamente."
    exit 1
else
    echo "[INFO] Docker já está instalado."
fi

# 2)  Testa conexão com o daemon Docker
if ! docker info &> /dev/null; then
  echo "[ERRO] Não foi possível conectar ao Docker daemon."
  echo "[INFO] Caso tenha feito a instalaçao recente do Docker, faça LOGIN novamente para consertar o erro."
  # Adiciona seu usuário ao grupo docker
  sudo usermod -aG docker $USER
  exit 1
fi

# 3) Instala o Mininet se não existir
if ! command -v mn &> /dev/null; then
    echo "[INFO] Instalando Mininet..."
    sudo apt-get update
    if [ "$OS_ID" = "kali" ]; then
        echo "[INFO] Instalando Mininet em modo não‐interativo..."
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" \
  mininet
    else
        sudo apt-get install -y mininet
    fi
else
    echo "[INFO] Mininet já está instalado."
fi

# 4) Instala o Open vSwitch se não estiver presente
if ! dpkg -l | grep -qw openvswitch-switch; then
    echo "[INFO] Instalando Open vSwitch..."
    if [ "$OS_ID" = "kali" ]; then
        echo "[INFO] Instalando OpenVSwitch em modo não‐interativo..."
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" \
  openvswitch-switch
    else
        sudo apt-get install -y openvswitch-switch
    fi
else
    echo "[INFO] Open vSwitch já está instalado."
fi

# Checa se o serviço openvswitch-switch está ativo
if systemctl is-active --quiet openvswitch-switch; then
    echo "[INFO] Serviço openvswitch-switch já está ativo."
else
    echo "[INFO] Serviço openvswitch-switch não está ativo. Habilitando e iniciando..."
    sudo systemctl enable --now openvswitch-switch
    echo "[OK] Serviço openvswitch-switch iniciado."
fi

# Função que verifica se a imagem Docker existe localmente; se não existir, faz o pull da imagem
pull_if_missing() {
  local image="$1"
  if ! docker image inspect "$image" &> /dev/null; then
    echo "[INFO] Imagem '$image' não encontrada. Baixando do Docker Hub..."
    docker pull "$image"
  else
    echo "[INFO] Imagem '$image' já está disponível localmente."
  fi
}

# Verifica e baixa as imagens necessárias (ONOS e Ryu)
pull_if_missing "onosproject/onos"
pull_if_missing "osrg/ryu"

# Função para limpar containers antigos
cleanup() {
  echo "[INFO] Limpando containers antigos..."
  # Remove containers antigos se existirem, para evitar conflitos
  # O '|| true' garante que o script continue mesmo que os containers não existam 
  docker rm -f onos-controller ryu-controller &> /dev/null || true
  echo "[INFO] Limpando cache Mininet..."
  sudo mn -c &> /dev/null || true
}

# Executa a limpeza antes de iniciar
cleanup

# Escolha do controlador
echo "Escolha o controlador SDN:"
echo "1 - ONOS"
echo "2 - Ryu"
read -p "Digite o número correspondente: " controller_choice

case $controller_choice in
  1)
    CONTROLLER_NAME="onos-controller"
    IMAGE_NAME="onosproject/onos"
    OF_PORT=6633
    REST_PORT=8181
    docker run -t -d --name $CONTROLLER_NAME -e ONOS_APPS="drivers,openflow,proxyarp,fwd,gui2" -p $REST_PORT:$REST_PORT -p $OF_PORT:$OF_PORT onosproject/onos
    echo "[INFO] Aguardando 30s para o ONOS iniciar..."
    sleep 30  # tempo extra para ONOS subir completamente
    #echo "[INFO] Ativando apps ONOS..."
    ;;
  2)
    CONTROLLER_NAME="ryu-controller"
    IMAGE_NAME="osrg/ryu"
    OF_PORT=6633
    docker run -itd --name $CONTROLLER_NAME -p $OF_PORT:$OF_PORT -p 8080:8080 $IMAGE_NAME ryu-manager ryu.app.simple_switch_13
    ;;
  *)
    echo "[ERRO] Opção inválida."
    exit 1
    ;;
esac

# Espera alguns segundos para o container subir corretamente
echo "[INFO] Aguardando inicialização do controlador..."
sleep 5

# Obtém o IP local (do host, pois Mininet está fora do Docker)
CONTROLLER_IP="127.0.0.1"

# Executa o Mininet conectado ao controlador
if [ "$SKIP_MININET" -eq 1 ]; then
   echo "[INFO] Topologia subida em modo no-Mininet. Encerrando provisionamento."
   exit 0
else
  echo "[INFO] Iniciando Mininet com topo simples e conexão ao controlador $CONTROLLER_IP:$OF_PORT"
  # modo interativo (CLI)
  sudo mn --controller=remote,ip=$CONTROLLER_IP,port=$OF_PORT --topo=tree,depth=2,fanout=2 --switch=ovsk,protocols=OpenFlow13
fi

# Executa uma limpeza antes de encerrar
cleanup

echo "[OK] Ambiente SDN finalizado."
