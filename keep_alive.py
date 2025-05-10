import os
import time
import logging
import threading
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ping_server():
    """Function to ping the server to keep it alive."""
    try:
        # Get the ping URL from environment or use default
        ping_url = os.environ.get("PING_URL", "http://localhost:5000/ping")
        response = requests.get(ping_url, timeout=10)
        
        if response.status_code == 200:
            logger.debug(f"Ping successful. Response: {response.text}")
            return True
        else:
            logger.warning(f"Ping failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error pinging server: {e}")
        return False

def keep_alive_ping():
    """Function to continuously ping the server at regular intervals."""
    # Get the ping interval from environment or use default (5 minutes)
    ping_interval = int(os.environ.get("PING_INTERVAL_SECONDS", 300))
    
    logger.info(f"Starting keep-alive service with interval of {ping_interval} seconds")
    
    while True:
        success = ping_server()
        
        if success:
            try:
                # We need to import here to avoid circular imports
                from models import BotStatus
                from app import app, db
                
                # Update the ping status in the database if possible
                with app.app_context():
                    status = BotStatus.query.order_by(BotStatus.id.desc()).first()
                    if status:
                        status.last_ping = datetime.now()
                        status.uptime = int(time.time() - status.start_time.timestamp())
                        db.session.commit()
                        logger.debug("Updated ping status in database")
                    else:
                        # Create a new status entry if none exists
                        status = BotStatus(
                            start_time=datetime.now(),
                            last_ping=datetime.now(),
                            uptime=0
                        )
                        db.session.add(status)
                        db.session.commit()
                        logger.debug("Created new ping status in database")
            except Exception as e:
                logger.error(f"Error updating ping status in database: {e}")
        
        # Sleep for the specified interval
        time.sleep(ping_interval)

def start_ping_service():
    """Start the ping service in a separate thread."""
    ping_thread = threading.Thread(target=keep_alive_ping)
    ping_thread.daemon = True
    ping_thread.start()
    logger.info("Ping service started in background thread")
    return ping_thread

if __name__ == "__main__":
    # If this file is run directly, start the ping service
    thread = start_ping_service()
    # Keep the main thread alive
    thread.join()
