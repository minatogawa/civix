import os
import sys
import threading
import time
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify
from logger import get_logger

load_dotenv()

logger = get_logger(__name__)

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


class CivixBot:
    def __init__(self):
        self.running = False
        self.discord_token = os.getenv("DISCORD_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        logger.info(
            "CiviX Bot initialized",
            discord_token_set=bool(self.discord_token),
            telegram_token_set=bool(self.telegram_token),
        )

    def start(self):
        """Start the bot service"""
        logger.info("Starting CiviX Bot service")
        self.running = True
        bot_status["running"] = True
        bot_status["last_activity"] = datetime.now().isoformat()

        try:
            # Simulate bot activity
            while self.running:
                self.heartbeat()
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logger.info("Bot stopped by user interrupt")
            self.stop()
        except Exception as e:
            logger.error(
                "Bot service error occurred",
                error=str(e),
                error_count=bot_status["error_count"] + 1,
                exc_info=True,
            )
            bot_status["error_count"] += 1
            self.stop()

    def heartbeat(self):
        """Update bot activity"""
        bot_status["last_activity"] = datetime.now().isoformat()
        logger.debug("Bot heartbeat - service running normally")

    def stop(self):
        """Stop the bot service"""
        logger.info("Stopping CiviX Bot service")
        self.running = False
        bot_status["running"] = False


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
