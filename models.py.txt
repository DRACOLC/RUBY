from datetime import datetime
from app import db
from sqlalchemy import Column, Integer, DateTime, String

class BotStatus(db.Model):
    """Model to store bot status information."""
    __tablename__ = 'bot_status'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.now)
    last_ping = Column(DateTime, nullable=True)
    uptime = Column(Integer, default=0)  # Uptime in seconds
    status = Column(String(50), default="active")
    
    def __repr__(self):
        return f"<BotStatus id={self.id} status={self.status} uptime={self.uptime}s>"

class ReportUsage(db.Model):
    """Model to track usage of report commands."""
    __tablename__ = 'report_usage'
    
    id = Column(Integer, primary_key=True)
    command = Column(String(20), nullable=False)  # baixa or fac
    code = Column(String(20), nullable=False)     # the report code used
    timestamp = Column(DateTime, default=datetime.now)
    user_id = Column(String(50), nullable=True)   # Telegram user ID if available
    
    def __repr__(self):
        return f"<ReportUsage id={self.id} command={self.command} code={self.code}>"
