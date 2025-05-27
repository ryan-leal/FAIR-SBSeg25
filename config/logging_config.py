import logging

# Configuracao básica da saida com o logging, altere aqui para mudar como os logs saem.
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('results/attack_tool.log'),
            logging.StreamHandler()
        ]
    )
