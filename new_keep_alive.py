from flask import Flask
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "Bot está ativo!"

def run():
    logger.info("Iniciando servidor web na porta 8080")
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Inicia o servidor web em uma thread separada para manter o bot ativo"""
    t = Thread(target=run)
    t.daemon = True  # Definir como daemon para encerrar quando o programa principal terminar
    t.start()
    logger.info("Servidor web iniciado em background thread")
    return t

if __name__ == "__main__":
    # Se este arquivo for executado diretamente, inicia o servidor
    thread = keep_alive()
    # Mantém a thread principal ativa
    thread.join()
