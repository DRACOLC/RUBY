import os
import json
import logging
import time
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the report templates
def load_templates():
    try:
        with open('report_templates.json', 'r', encoding='utf-8') as file:
            templates = json.load(file)
        return templates
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        # Provide default templates if file can't be loaded
        return {
            "baixa": {
                "103": {
                    "title": "Chuva",
                    "description": "A execução do serviço foi impossibilitada devido à ocorrência de chuvas intensas no momento da visita técnica. A atividade será reagendada conforme as condições climáticas permitirem. Encaminhado ao COP para validação da visita."
                }
            },
            "fac": {
                "103": {
                    "title": "- Chuva",
                    "fato": "- Chuva",
                    "causa": "- A execução do serviço foi impossibilitada devido à ocorrência de chuvas intensas no momento da visita técnica.",
                    "acao": "- A atividade será reagendada conforme as condições climáticas permitirem.",
                    "obs": "✅ Encaminhado ao COP para validação da visita.",
                    "contato": "- ",
                    "atendido": "nome"
                }
            }
        }

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Olá! Sou o Bot de Relatórios de Serviço.\n\n"
        "Comandos disponíveis:\n"
        "/baixa [número] - Gera descrição detalhada da baixa\n"
        "/fac [número] - Gera Ficha de Atendimento ao Cliente\n"
        "/restart - Reinicia o bot (apenas para administradores)\n"
        "/help - Mostra ajuda detalhada sobre os comandos"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    help_text = (
        "📋 *Ajuda do Bot de Relatórios* 📋\n\n"
        "*O que este bot faz?*\n"
        "Este bot foi desenvolvido para auxiliar técnicos e equipes de suporte na geração rápida e padronizada "
        "de relatórios de atendimento, utilizando os códigos de baixa e FAC (Ficha de Atendimento ao Cliente).\n\n"
        
        "📌 *Comandos disponíveis*\n\n"
        
        "*/baixa [número]*\n"
        "Gera a descrição detalhada da baixa correspondente ao número informado.\n"
        "Exemplo:\n"
        "`/baixa 103`\n"
        "Resposta:\n"
        "```\n103 - Chuva\nA execução do serviço foi impossibilitada devido à ocorrência de chuvas intensas no momento da visita técnica. A atividade será reagendada conforme as condições climáticas permitirem. Encaminhado ao COP para validação da visita.```\n\n"
        
        "*/fac [número]*\n"
        "Gera a Ficha de Atendimento ao Cliente (FAC) correspondente ao número informado.\n"
        "Exemplo:\n"
        "`/fac 103`\n"
        "Resposta:\n"
        "```\nFAC-103\nCONTRATO: [número do contrato]\nFATO: Chuva\nCAUSA: A execução do serviço foi impossibilitada devido à ocorrência de chuvas intensas no momento da visita técnica.\nAÇÃO: A atividade será reagendada conforme as condições climáticas permitirem.\nOBS: ✅ Encaminhado ao COP para validação da visita.```\n\n"
        
        "*/restart*\n"
        "Reinicia o bot em caso de problemas ou após atualizações.\n"
        "Este comando só está disponível para administradores."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def baixa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a 'baixa' report."""
    templates = load_templates()
    
    if not context.args:
        await update.message.reply_text(
            "Por favor, forneça o número da baixa. Exemplo: `/baixa 103`",
            parse_mode='Markdown'
        )
        return
    
    code = context.args[0]
    baixa_templates = templates.get("baixa", {})
    
    if code in baixa_templates:
        template = baixa_templates[code]
        response = (
            f"{code} - {template['title']}\n"
            f"{template['description']}"
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(
            "Código de baixa não encontrado. Verifique o número e tente novamente."
        )

async def fac_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a 'FAC' report."""
    templates = load_templates()
    
    if not context.args:
        await update.message.reply_text(
            "Por favor, forneça o número da FAC. Exemplo: `/fac 103`",
            parse_mode='Markdown'
        )
        return
    
    code = context.args[0]
    fac_templates = templates.get("fac", {})
    
    if code in fac_templates:
        template = fac_templates[code]
        response = (
            f"FAC-{code}\n"
            f"CONTRATO: [número do contrato]\n"
            f"FATO: {template['fato']}\n"
            f"CAUSA: {template['causa']}\n"
            f"AÇÃO: {template['acao']}\n"
            f"OBS: {template['obs']}"
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(
            "Código de FAC não encontrado. Verifique o número e tente novamente."
        )
        
async def grupo_baixa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Versão otimizada do comando baixa para grupos."""
    templates = load_templates()
    
    if not context.args:
        await update.message.reply_text(
            "Por favor, forneça o número da baixa. Exemplo: `/grupo_baixa 103`",
            parse_mode='Markdown'
        )
        return
    
    code = context.args[0]
    baixa_templates = templates.get("baixa", {})
    
    if code in baixa_templates:
        template = baixa_templates[code]
        # Versão simplificada para grupos - apenas título e código
        response = f"📋 *{code} - {template['title']}*\n"
        
        # Adiciona apenas as primeiras 100 caracteres da descrição e indica que há mais
        if len(template['description']) > 100:
            response += f"{template['description'][:100]}...\n\n"
            response += "_Use o comando /baixa para ver a descrição completa_"
        else:
            response += template['description']
            
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "Código de baixa não encontrado. Verifique o número e tente novamente."
        )

async def grupo_fac_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Versão otimizada do comando FAC para grupos."""
    templates = load_templates()
    
    if not context.args:
        await update.message.reply_text(
            "Por favor, forneça o número da FAC. Exemplo: `/grupo_fac 103`",
            parse_mode='Markdown'
        )
        return
    
    code = context.args[0]
    fac_templates = templates.get("fac", {})
    
    if code in fac_templates:
        template = fac_templates[code]
        # Versão simplificada para grupos - apenas informações essenciais
        response = (
            f"*FAC-{code}*\n"
            f"FATO: {template['fato']}\n"
            f"AÇÃO: {template['acao']}\n\n"
            f"_Use o comando /fac para ver todos os detalhes_"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "Código de FAC não encontrado. Verifique o número e tente novamente."
        )

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reinicia o bot quando o comando /restart é enviado."""
    # Lista de IDs de administradores autorizados a reiniciar o bot
    # Por segurança, você pode definir IDs específicos aqui
    admin_ids = [1219600399]  # Substitua pelo ID do administrador real
    
    user_id = update.effective_user.id
    
    if user_id in admin_ids:
        await update.message.reply_text("Reiniciando o bot... Aguarde alguns instantes.")
        logger.info(f"Bot reiniciado por solicitação do usuário ID: {user_id}")
        
        # Executa o processo de reinicialização
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        await update.message.reply_text("Desculpe, você não tem permissão para reiniciar o bot.")
        logger.warning(f"Tentativa de reinício não autorizada pelo usuário ID: {user_id}")

async def update_bot_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update the bot status in the database to indicate it's still alive."""
    try:
        # We need to import here to avoid circular imports
        from models import BotStatus
        from app import db
        
        # Create a new status entry or update the existing one
        status = BotStatus.query.order_by(BotStatus.id.desc()).first()
        if status:
            status.last_ping = datetime.now()
            status.uptime = int(time.time() - status.start_time.timestamp())
        else:
            status = BotStatus(
                start_time=datetime.now(),
                last_ping=datetime.now(),
                uptime=0
            )
            db.session.add(status)
        
        db.session.commit()
        logger.debug("Bot status updated successfully")
    except Exception as e:
        logger.error(f"Error updating bot status: {e}")

def start_bot():
    """Start the Telegram bot."""
    try:
        # Get token from environment variable
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("No Telegram bot token provided. Please set the TELEGRAM_BOT_TOKEN environment variable.")
            return
        
        import asyncio
        
        # Function to run the bot asynchronously
        async def run_async_bot():
            try:
                # Create the Application
                application = Application.builder().token(token).build()
        
                # Register command handlers
                application.add_handler(CommandHandler("start", start))
                application.add_handler(CommandHandler("help", help_command))
                application.add_handler(CommandHandler("baixa", baixa_command))
                application.add_handler(CommandHandler("fac", fac_command))
                application.add_handler(CommandHandler("grupo_baixa", grupo_baixa_command))
                application.add_handler(CommandHandler("grupo_fac", grupo_fac_command))
                application.add_handler(CommandHandler("restart", restart_command))
                
                # Register job to update bot status
                job_queue = application.job_queue
                job_queue.run_repeating(update_bot_status, interval=300, first=10)  # Every 5 minutes
                
                # Start the Bot
                logger.info("Starting bot polling...")
                await application.initialize()
                await application.start()
                await application.updater.start_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=False,  # Process any pending updates
                    timeout=30,  # Longer timeout for better reliability
                    poll_interval=0.5  # Check more frequently
                )
                
                # Log that the bot is running
                logger.info("Bot polling started successfully and is now running.")
                
                # Run the bot forever in background
                running = True
                while running:
                    try:
                        # Just keep the bot running but don't block
                        await asyncio.sleep(5)
                    except KeyboardInterrupt:
                        running = False
            except TelegramError as e:
                logger.error(f"Telegram Error: {e}")
            except Exception as e:
                logger.error(f"Error in async bot: {e}")
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start the bot and keep it running in the background
        logger.info("Starting bot in background thread...")
        
        # This is a critical change: we need to create a thread that runs the event loop
        # This way, the main thread can continue and serve Flask requests
        import threading
        
        def run_bot_loop():
            loop.run_until_complete(run_async_bot())
            logger.info("Bot background thread has completed")
        
        # Start the bot in a dedicated thread
        bot_thread = threading.Thread(target=run_bot_loop)
        bot_thread.daemon = True  # Allow Python to exit even if this thread is running
        bot_thread.start()
        
        logger.info("Bot background thread started")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    start_bot()
