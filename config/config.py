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
    'IP': '127.0.0.1',
    'INTERFACE': 'h1-eth0',
    'MAX_TIME': '30'
}
