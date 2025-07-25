import asyncio
import os
import sys
import threading
import time
from datetime import datetime

from database import create_app
from dotenv import load_dotenv
from flask import Flask, jsonify
from logger import get_logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai_processor_simple import DemandProcessor

load_dotenv()

logger = get_logger(__name__)

# Bot status tracking
start_time = time.time()

# Health check server for bot service
health_app = Flask(__name__)


@health_app.route("/health")
def health():
    """Health check endpoint for bot service"""
    logger.info("Bot health check endpoint accessed")
    return jsonify(
        {
            "status": "healthy",
            "service": "civix-bot",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time,
        }
    )


# Bot status
bot_status = {"running": False, "last_activity": None, "error_count": 0}

start_time = time.time()

# Criar contexto Flask para acesso ao banco
flask_app = create_app()
app_context = flask_app.app_context()
app_context.push()

processor = DemandProcessor()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 Olá! Bem-vindo ao CiviX Bot!\n\n"
        "Eu posso ajudar você com:\n"
        "• /help - Ver comandos disponíveis\n"
        "• /status - Status do sistema\n"
        "• Envie qualquer mensagem para conversar!"
    )
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🤖 *Comandos do CiviX Bot:*

/start - Iniciar o bot
/help - Mostrar esta ajuda
/status - Status do sistema

💬 Você também pode enviar mensagens normais para conversar comigo!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} requested help")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    status_text = f"""
📊 *Status do CiviX:*

🟢 Bot: Online
⏰ Uptime: {time.time() - start_time:.0f}s
📝 Última atividade: {bot_status['last_activity']}
❌ Erros: {bot_status['error_count']}
    """
    await update.message.reply_text(status_text, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} requested status")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with AI processing"""
    user_message = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Usuário"

    logger.info(f"Received message from user {user_id} ({user_name}): {user_message}")

    # Enviar mensagem de processamento
    processing_msg = await update.message.reply_text("🤖 Processando sua mensagem...")

    try:
        # Processar com OpenAI e salvar no banco
        result = await processor.process_message(user_message, user_id, user_name)

        if result:
            # Demanda foi processada com sucesso
            demanda_id = result["demanda_id"]
            extracted_data = result["extracted_data"]

            response = "✅ **Demanda registrada com sucesso!**\n\n"
            response += f"📝 **ID:** {demanda_id}\n"
            response += (
                f"🏷️ **Tipo:** {extracted_data.get('tipo_demanda', 'N/A').title()}\n"
            )

            if extracted_data.get("bairro"):
                response += f"📍 **Bairro:** {extracted_data['bairro']}\n"

            if extracted_data.get("descricao_curta"):
                response += f"📋 **Resumo:** {extracted_data['descricao_curta']}\n"

            urgencia = extracted_data.get("urgencia", 1)
            if urgencia >= 4:
                response += f"🚨 **Prioridade:** Alta (Urgência {urgencia}/5)\n"
            elif urgencia >= 3:
                response += f"⚠️ **Prioridade:** Média (Urgência {urgencia}/5)\n"
            else:
                response += f"ℹ️ **Prioridade:** Baixa (Urgência {urgencia}/5)\n"

            response += "\n🔄 **Status:** Em análise\n"
            response += "📊 Você pode acompanhar o andamento pelo sistema web!"

        else:
            # Não foi identificada como demanda ou houve erro
            response = f"💬 Mensagem recebida: '{user_message}'\n\n"
            response += (
                "ℹ️ Sua mensagem não foi identificada como uma demanda específica. "
            )
            response += "Se precisar reportar um problema da comunidade, tente ser mais específico sobre:\n"
            response += "• Local do problema\n"
            response += "• Tipo de problema (zeladoria, saúde, etc.)\n"
            response += "• Descrição detalhada\n\n"
            response += "Ou use os comandos:\n/help - Ver ajuda\n/status - Ver status do sistema"

        # Atualizar mensagem de processamento
        await processing_msg.edit_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(
            f"Error processing message from user {user_id}", error=str(e), exc_info=True
        )
        await processing_msg.edit_text(
            "❌ Erro interno no processamento. Tente novamente em alguns minutos."
        )

    # Update activity
    bot_status["last_activity"] = datetime.now().isoformat()


class CivixBot:
    def __init__(self):
        self.running = False
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.application = None

        if not self.telegram_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        logger.info(
            "CiviX Bot initialized", telegram_token_set=bool(self.telegram_token)
        )

    async def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("status", status_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        logger.info("Bot handlers configured")

    async def start_bot(self):
        """Start the Telegram bot"""
        self.application = Application.builder().token(self.telegram_token).build()
        await self.setup_handlers()

        logger.info("Starting Telegram bot polling...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        self.running = True
        bot_status["running"] = True
        bot_status["last_activity"] = datetime.now().isoformat()

        # Keep the bot running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user interrupt")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the bot service"""
        logger.info("Stopping CiviX Bot service")
        self.running = False
        bot_status["running"] = False

        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

    def start(self):
        """Start the bot service (wrapper for async)"""
        import asyncio

        try:
            asyncio.run(self.start_bot())
        except Exception as e:
            logger.error("Failed to start bot", error=str(e), exc_info=True)
            bot_status["error_count"] += 1
            raise


def run_health_server():
    """Run health check server in separate thread"""
    logger.info("Starting bot health check server", port=8080)
    health_app.run(host="0.0.0.0", port=8080, debug=False)


if __name__ == "__main__":
    logger.info("Initializing CiviX Bot application")

    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info("Health check server thread started")

    # Start the bot
    bot = CivixBot()

    try:
        bot.start()
    except Exception as e:
        logger.error("Failed to start bot service", error=str(e), exc_info=True)
        sys.exit(1)
