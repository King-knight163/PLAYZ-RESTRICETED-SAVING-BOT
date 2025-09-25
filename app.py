from flask import Flask
import threading
import os
import time
import sys

app = Flask(__name__)

# Bot status tracking
bot_status = {"running": False, "started": False, "error": None, "logs": []}

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
def logs():
    return {'logs': bot_status.get('logs', [])}

def run_bot():
    """Run Telegram bot in background"""
    global bot_status
    try:
        bot_status["logs"].append('🔄 Starting Telegram Bot Thread...')
        print('🔄 Starting Telegram Bot Thread...')
        bot_status["started"] = True
        
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import और initialize bot
        from bot import Bot
        bot_status["logs"].append('📦 Bot class imported successfully')
        print('📦 Bot class imported successfully')
        
        bot = Bot()
        bot_status["logs"].append('🤖 Bot instance created')
        print('🤖 Bot instance created')
        bot_status["running"] = True
        
        # Run the bot
        bot_status["logs"].append('🚀 Starting bot.run()...')
        print('🚀 Starting bot.run()...')
        bot.run()
        
    except ImportError as e:
        error_msg = f'Import Error: {e}'
        bot_status["logs"].append(f'❌ {error_msg}')
        print(f'❌ {error_msg}')
        bot_status["error"] = error_msg
        bot_status["running"] = False
        
    except Exception as e:
        error_msg = f'Bot Runtime Error: {e}'
        bot_status["logs"].append(f'❌ {error_msg}')
        print(f'❌ {error_msg}')
        bot_status["error"] = error_msg
        bot_status["running"] = False

if __name__ == "__main__":
    print('🌟 PLAY-Z Restricted Saving Bot Starting...')
    print('🔧 Initializing Flask + Bot Application...')
    
    # Start bot in background thread
    print('📡 Creating bot thread...')
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    print('⏳ Waiting for bot initialization...')
    time.sleep(5)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    print(f'🌐 Starting Flask server on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=False)
