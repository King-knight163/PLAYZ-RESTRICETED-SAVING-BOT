from flask import Flask
import threading
import os
import time
import sys
import logging

app = Flask(__name__)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot status tracking
bot_status = {
    "running": False, 
    "started": False, 
    "error": None, 
    "logs": [],
    "import_success": False
}

@app.route('/')
def hello_world():
    return 'PLAY-Z Restricted Saving Bot is Running! 🚀'

@app.route('/status')
def status():
    return {
        'status': 'active',
        'message': 'Bot is running successfully',
        'service': 'PLAY-Z Restricted Saving Bot',
        'bot_status': bot_status
    }

@app.route('/logs')
def get_logs():
    return {'logs': bot_status.get('logs', [])}

def add_log(message):
    """Add log to both console and bot_status"""
    print(message)
    logger.info(message)
    bot_status["logs"].append(message)
    # Keep only last 50 logs
    if len(bot_status["logs"]) > 50:
        bot_status["logs"] = bot_status["logs"][-50:]

def run_bot():
    """Run Telegram bot in background"""
    global bot_status
    try:
        add_log('🔄 Starting Telegram Bot Thread...')
        bot_status["started"] = True
        
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        add_log(f'📁 Added {current_dir} to Python path')
        
        # Test import first
        add_log('📦 Testing imports...')
        try:
            from config import API_ID, API_HASH, BOT_TOKEN
            add_log('✅ Config imported successfully')
            
            from database.db import db
            add_log('✅ Database module imported successfully')
            
            from bot import Bot
            add_log('✅ Bot class imported successfully')
            bot_status["import_success"] = True
            
        except ImportError as e:
            error_msg = f'Import Error: {str(e)}'
            add_log(f'❌ {error_msg}')
            bot_status["error"] = error_msg
            bot_status["running"] = False
            bot_status["import_success"] = False
            return
        
        # Create and run bot
        add_log('🤖 Creating Bot instance...')
        bot = Bot()
        add_log('✅ Bot instance created successfully')
        
        bot_status["running"] = True
        add_log('🚀 Starting bot.run()...')
        
        # This will block until bot stops
        bot.run()
        
    except Exception as e:
        error_msg = f'Bot Runtime Error: {str(e)}'
        add_log(f'❌ {error_msg}')
        bot_status["error"] = error_msg
        bot_status["running"] = False

if __name__ == "__main__":
    add_log('🌟 PLAY-Z Restricted Saving Bot Starting...')
    add_log('🔧 Initializing Flask + Bot Application...')
    
    # Start bot in background thread
    add_log('📡 Creating bot thread...')
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    add_log('✅ Bot thread started')
    
    # Give bot time to start
    add_log('⏳ Waiting for bot initialization...')
    time.sleep(5)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    add_log(f'🌐 Starting Flask server on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=False)
