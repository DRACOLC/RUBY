import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

@app.route('/')
def index():
    """Homepage for the ping server"""
    return render_template('index.html')

@app.route('/ping')
def ping():
    """Ping endpoint to keep the service awake"""
    logger.debug("Ping received")
    return 'Pong! Bot is active', 200

@app.route('/status')
def status():
    """Return the current status of the bot"""
    # Import here to avoid circular imports
    from models import BotStatus
    status = BotStatus.query.order_by(BotStatus.id.desc()).first()
    if status:
        return {
            'status': 'active',
            'last_ping': status.last_ping.isoformat() if status.last_ping else None,
            'uptime': status.uptime
        }
    return {'status': 'unknown'}, 404

def run_bot():
    """Function to run the Telegram bot in a separate thread"""
    from bot import start_bot
    logger.info("Starting bot thread")
    start_bot()

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        import models
        db.create_all()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
