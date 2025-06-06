from app import app
import os
import threading
import logging
from bot import start_bot
from keep_alive import start_ping_service
import new_keep_alive  # Importa o novo sistema de keep_alive

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_bot():
    """Function to run the Telegram bot in a separate thread"""
    logger.info("Starting bot thread")
    start_bot()

# Inicializa o servidor keep-alive na porta 8080
new_keep_alive.keep_alive()
logger.info("Iniciado o servidor web keep-alive na porta 8080")

# Initialize database and start services when in app context
with app.app_context():
    # Create all database tables
    import models
    from app import db
    db.create_all()
    
    # Start the ping service in a thread (antigo sistema, mantido para compatibilidade)
    ping_thread = threading.Thread(target=start_ping_service)
    ping_thread.daemon = True
    ping_thread.start()
    logger.info("Started ping service")
    
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Started bot service")

if __name__ == '__main__':
    # Run the Flask app if executed directly
    app.run(host='0.0.0.0', port=5000, debug=True)
