# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH, BOT_TOKEN
import asyncio

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            print(f'✅ Bot Started Successfully! @{me.username}')
            print('🚀 Powered By @VJ_Botz')
        except FloodWait as e:
            print(f'⚠️ FloodWait Error: Waiting {e.value} seconds...')
            await asyncio.sleep(e.value)
            await self.start()
        except Exception as e:
            print(f'❌ Error starting bot: {e}')
            raise e

    async def stop(self, *args):
        await super().stop()
        print('🛑 Bot Stopped - Bye!')

if __name__ == "__main__":
    print("🤖 Running bot directly...")
    Bot().run()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
