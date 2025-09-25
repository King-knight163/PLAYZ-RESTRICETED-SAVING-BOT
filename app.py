from flask import Flask
import threading
import os
import sys
import asyncio
from bot import Bot

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'PLAY-Z Restricted Saving Bot is Running! 🚀'

@app.route('/status')
def status():
    return {
        'status': 'active', 
        'message': 'Bot is running successfully',
        'service': 'PLAY-Z Restricted Saving Bot'
    }

def run_bot():
    """Run Telegram bot in background"""
    try:
        print('🔄 Starting Telegram Bot...')
        bot = Bot()
        bot.run()
    except Exception as e:
        print(f'❌ Bot Error: {e}')

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask app for Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
