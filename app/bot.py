import logging
import sys
import time
from datetime import datetime
from flask import Flask, jsonify
import threading
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check server for bot service
health_app = Flask(__name__)

@health_app.route('/health')
def health():
    """Health check endpoint for bot service"""
    return jsonify({
        'status': 'healthy',
        'service': 'civix-bot',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time
    })

# Bot status
bot_status = {
    'running': False,
    'last_activity': None,
    'error_count': 0
}

start_time = time.time()

class CivixBot:
    def __init__(self):
        self.running = False
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        
    def start(self):
        """Start the bot service"""
        logger.info("Starting CiviX Bot...")
        self.running = True
        bot_status['running'] = True
        bot_status['last_activity'] = datetime.now().isoformat()
        
        try:
            # Simulate bot activity
            while self.running:
                self.heartbeat()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            bot_status['error_count'] += 1
            self.stop()
    
    def heartbeat(self):
        """Update bot activity"""
        bot_status['last_activity'] = datetime.now().isoformat()
        logger.info("Bot heartbeat - service running")
    
    def stop(self):
        """Stop the bot service"""
        logger.info("Stopping CiviX Bot...")
        self.running = False
        bot_status['running'] = False

def run_health_server():
    """Run health check server in separate thread"""
    health_app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Start the bot
    bot = CivixBot()
    
    try:
        bot.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)