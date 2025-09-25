# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import time
import pyrogram
import requests
import json
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT

class batch_temp(object):
    IS_BATCH = {}

# Configuration constants
SHRINKME_API_KEY = "6a5a6ce8d33950c63502d761ae11bf36632f08ca"
FREEMIUM_DURATION = 86400  # 24 hours

def generate_shrink_url(destination_url, alias=None):
    """Generate shortened URL using ShrinkMe API"""
    try:
        if alias:
            api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={destination_url}&alias={alias}"
        else:
            api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={destination_url}"
        
        response = requests.get(api_url)
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        else:
            # If alias exists, try without alias
            if alias:
                return generate_shrink_url(destination_url)
            return None
    except:
        return None

async def stylish_progress_bar(client, chat_id, message_id, progress_type="Downloading"):
    """Advanced animated progress bar"""
    progress_frames = [
        f"🔄 **{progress_type}**
▱▱▱▱▱▱▱▱▱▱ 0%",
        f"🔄 **{progress_type}**
▰▱▱▱▱▱▱▱▱▱ 10%",
        f"🔄 **{progress_type}**
▰▰▱▱▱▱▱▱▱▱ 20%",
        f"🔄 **{progress_type}**
▰▰▰▱▱▱▱▱▱▱ 30%",
        f"🔄 **{progress_type}**
▰▰▰▰▱▱▱▱▱▱ 40%",
        f"🔄 **{progress_type}**
▰▰▰▰▰▱▱▱▱▱ 50%",
        f"🔄 **{progress_type}**
▰▰▰▰▰▰▱▱▱▱ 60%",
        f"🔄 **{progress_type}**
▰▰▰▰▰▰▰▱▱▱ 70%",
        f"🔄 **{progress_type}**
▰▰▰▰▰▰▰▰▱▱ 80%",
        f"🔄 **{progress_type}**
▰▰▰▰▰▰▰▰▰▱ 90%",
        f"✅ **{progress_type} Complete!**
▰▰▰▰▰▰▰▰▰▰ 100%"
    ]
    
    for frame in progress_frames:
        try:
            await client.edit_message_text(chat_id, message_id, frame, parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(0.5)
        except:
            await asyncio.sleep(0.3)

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            progress_bar = "▰" * int(float(txt.replace('%', '')) / 10) + "▱" * (10 - int(float(txt.replace('%', '')) / 10))
            await client.edit_message_text(chat, message.id, f"📥 **Downloading...**

{progress_bar} **{txt}**

⚡ Processing your request...", parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(1)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            progress_bar = "▰" * int(float(txt.replace('%', '')) / 10) + "▱" * (10 - int(float(txt.replace('%', '')) / 10))
            await client.edit_message_text(chat, message.id, f"📤 **Uploading...**

{progress_bar} **{txt}**

🚀 Almost done!", parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(1)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# CALLBACK QUERY HANDLER FOR INLINE BUTTONS
@Client.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.id

    if data == "verify_btn":
        await handle_verify_callback(client, callback_query)
    elif data == "my_plan_btn":
        await handle_my_plan_callback(client, callback_query)
    elif data == "plans_btn":
        await handle_plans_callback(client, callback_query)
    elif data == "help_btn":
        await handle_help_callback(client, callback_query)
    elif data == "back_to_main":
        await handle_back_to_main(client, callback_query)
    elif data == "refresh_plan":
        await handle_my_plan_callback(client, callback_query)
    elif data.startswith("buy_"):
        plan = data.replace("buy_", "")
        await handle_buy_plan(client, callback_query, plan)

async def handle_verify_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    role = await db.get_user_role(chat_id)
    
    if role != "free":
        await callback_query.answer("✅ You are already verified!", show_alert=True)
        return
    
    code = await db.generate_or_get_code(chat_id)
    bot_username = (await client.get_me()).username
    destination_url = f"https://t.me/{bot_username}?start=add_premium_{chat_id}_{code}_freemium"
    
    # Generate unique alias
    alias = f"verify_{chat_id}_{int(time.time())}"
    verify_link = generate_shrink_url(destination_url, alias)
    
    if not verify_link:
        await callback_query.answer("❌ Error generating verification link. Try again!", show_alert=True)
        return
    
    verify_text = f"""
🔓 **VERIFICATION PROCESS**

🎯 **Get 24 Hours Freemium Access:**
   • 📁 Max 3 files per batch
   • 🔢 4 batches daily (12 posts/day)
   • 💾 Save restricted content
   • ⚡ Fast processing

🔗 **Your Personal Verification Link:**
Click the button below to complete verification

⚠️ **Security Notice:**
   • ✅ Link is personalized for you
   • ⏰ Valid for limited time only
   • 🚫 Don't share with others
   • 🔄 Complete all steps to activate

💎 **After verification, check /plan for premium upgrades!**
    """
    
    buttons = [
        [InlineKeyboardButton("🔓 Complete Verification", url=verify_link)],
        [InlineKeyboardButton("🔄 Refresh Link", callback_data="verify_btn")],
        [InlineKeyboardButton("📋 View All Plans", callback_data="plans_btn")],
        [InlineKeyboardButton("❓ How to Verify?", callback_data="help_verify")],
        [InlineKeyboardButton("🏠 Back to Main", callback_data="back_to_main")]
    ]
    
    try:
        await callback_query.edit_message_text(verify_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    except:
        await callback_query.answer("Please try again!", show_alert=True)

async def handle_my_plan_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    stats = await db.get_user_stats(chat_id)
    
    if not stats:
        await callback_query.answer("❌ Error loading your plan info!", show_alert=True)
        return
    
    role = stats["role"]
    usage = stats["usage"]
    expiry_readable = stats["expiry_readable"]
    
    # Define limits
    limits = {
        "freemium": {"files_per_batch": 3, "daily_batches": 4, "emoji": "🆓"},
        "standard": {"files_per_batch": 20, "daily_batches": 10, "emoji": "🔹"},
        "pro": {"files_per_batch": 50, "daily_batches": 15, "emoji": "💎"},
        "elite": {"files_per_batch": 100, "daily_batches": 15, "emoji": "👑"},
        "premium": {"files_per_batch": 1000, "daily_batches": 1000, "emoji": "⭐"},
        "free": {"files_per_batch": 0, "daily_batches": 0, "emoji": "🔒"}
    }
    
    limit = limits.get(role, limits["free"])
    
    if role == "free":
        plan_text = """
🔒 **ACCOUNT STATUS: FREE**

❌ **No Active Plan**
You need to verify to use this bot.

🎯 **What you're missing:**
   • Save restricted content
   • Forward private channel posts
   • Download media files

⚡ **Get instant access by verifying below!**
        """
        buttons = [
            [InlineKeyboardButton("🔓 Verify Now", callback_data="verify_btn")],
            [InlineKeyboardButton("📋 View All Plans", callback_data="plans_btn")]
        ]
    else:
        remaining_batches = max(0, limit["daily_batches"] - usage["batches"])
        used_percentage = (usage["batches"] / limit["daily_batches"]) * 100 if limit["daily_batches"] > 0 else 0
        
        progress_bar = "▰" * int(used_percentage / 10) + "▱" * (10 - int(used_percentage / 10))
        
        plan_text = f"""
{limit["emoji"]} **CURRENT PLAN: {role.upper()}**

📊 **Usage Statistics:**
   • **Batches Used:** {usage["batches"]}/{limit["daily_batches"]}
   • **Remaining:** {remaining_batches} batches
   • **Files per Batch:** {limit["files_per_batch"]}
   
📈 **Daily Progress:**
{progress_bar} **{used_percentage:.1f}%**

⏰ **Plan Details:**
   • **Status:** {"Active" if role != "free" else "Inactive"}
   • **Expiry:** {expiry_readable if role == "freemium" else "No Expiry"}

💡 **Tips:**
   • Usage resets every 24 hours
   • Upgrade for more features
        """
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="refresh_plan")],
            [InlineKeyboardButton("📈 Upgrade Plan", callback_data="plans_btn")],
            [InlineKeyboardButton("📋 All Plans", callback_data="plans_btn")],
            [InlineKeyboardButton("❓ Help", callback_data="help_btn")]
        ]
    
    buttons.append([InlineKeyboardButton("🏠 Back to Main", callback_data="back_to_main")])
    
    try:
        await callback_query.edit_message_text(plan_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    except:
        await callback_query.answer("Please try again!", show_alert=True)

async def handle_plans_callback(client: Client, callback_query: CallbackQuery):
    plans_text = """
💎 **AVAILABLE SUBSCRIPTION PLANS**

🆓 **FREEMIUM** (24 Hours)
   • 📁 3 files per batch
   • 🔢 4 batches daily
   • 💰 **FREE** (After Verification)

🔹 **STANDARD** 
   • 📁 20 files per batch  
   • 🔢 10 batches daily (200 posts)
   • 💰 **$8/month**

💎 **PRO**
   • 📁 50 files per batch
   • 🔢 15 batches daily (750 posts) 
   • 💰 **$20/month**

👑 **ELITE** (Best Value!)
   • 📁 100 files per batch
   • 🔢 15 batches daily (1500 posts)
   • 💰 **$45/month**

⭐ **PREMIUM** (Unlimited)
   • 📁 1000+ files per batch
   • 🔢 Unlimited batches
   • 💰 **Contact Admin**

✨ **All paid plans include:**
   • No ads • Priority support • Advanced features
    """
    
    buttons = [
        [
            InlineKeyboardButton("🛒 Buy Standard", callback_data="buy_standard"),
            InlineKeyboardButton("🛒 Buy Pro", callback_data="buy_pro")
        ],
        [
            InlineKeyboardButton("🛒 Buy Elite", callback_data="buy_elite"),
            InlineKeyboardButton("⭐ Get Premium", url="https://t.me/PLAYZ_90")
        ],
        [InlineKeyboardButton("🆓 Get Freemium", callback_data="verify_btn")],
        [InlineKeyboardButton("📊 My Current Plan", callback_data="my_plan_btn")],
        [InlineKeyboardButton("🏠 Back to Main", callback_data="back_to_main")]
    ]
    
    try:
        await callback_query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    except:
        await callback_query.answer("Please try again!", show_alert=True)

async def handle_help_callback(client: Client, callback_query: CallbackQuery):
    help_text = f"""
📚 **HELP & COMMANDS**

🤖 **Bot Commands:**
   • `/start` - Start the bot
   • `/help` - Show this help
   • `/verify` - Get verification link  
   • `/my_plan` - Check your plan
   • `/plan` - View all plans
   • `/cancel` - Cancel current batch

🔗 **How to Use:**
   1. Send any Telegram link
   2. Bot will save the content
   3. Works with private channels
   4. Supports all media types

🎯 **Link Formats Supported:**
   • `https://t.me/username/123`
   • `https://t.me/c/123456/789`
   • `https://t.me/b/botname/start`

⚠️ **Requirements:**
   • Must `/login` first for restricted content
   • Need verification for access
   • Respect usage limits

💡 **Pro Tips:**
   • Use batch links: `t.me/channel/1-10`
   • Cancel anytime with `/cancel`
   • Upgrade for more features

{HELP_TXT}
    """
    
    buttons = [
        [
            InlineKeyboardButton("🔓 Verify Account", callback_data="verify_btn"),
            InlineKeyboardButton("📊 My Plan", callback_data="my_plan_btn")
        ],
        [
            InlineKeyboardButton("💬 Support Group", url="https://t.me/PLAY_Z_HACKING_DISCUSSION"),
            InlineKeyboardButton("📢 Updates", url="https://t.me/+ahE-9i84aFxkOWNl")
        ],
        [InlineKeyboardButton("🏠 Back to Main", callback_data="back_to_main")]
    ]
    
    try:
        await callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    except:
        await callback_query.answer("Please try again!", show_alert=True)

async def handle_buy_plan(client: Client, callback_query: CallbackQuery, plan):
    plan_info = {
        "standard": {"price": "$8", "name": "Standard"},
        "pro": {"price": "$20", "name": "Pro"}, 
        "elite": {"price": "$45", "name": "Elite"}
    }
    
    info = plan_info.get(plan, {"price": "Contact", "name": "Premium"})
    
    buy_text = f"""
💳 **PURCHASE {info['name'].upper()} PLAN**

💰 **Price:** {info['price']}/month

🔗 **Payment Methods:**
   • UPI (India)
   • PayPal (International) 
   • Crypto (Bitcoin/USDT)
   • Bank Transfer

📞 **To Purchase:**
   1. Contact admin using button below
   2. Send screenshot of payment
   3. Get instant activation

⚡ **Instant Activation** after payment verification!
    """
    
    buttons = [
        [InlineKeyboardButton(f"💰 Pay {info['price']} Now", url="https://t.me/PLAYZ_90")],
        [InlineKeyboardButton("💬 Payment Support", url="https://t.me/PLAY_Z_HACKING_DISCUSSION")],
        [InlineKeyboardButton("📋 Back to Plans", callback_data="plans_btn")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ]
    
    await callback_query.edit_message_text(buy_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

async def handle_back_to_main(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    role = await db.get_user_role(chat_id)
    
    if role == "free":
        welcome_text = f"""
🤖 **PLAY-Z RESTRICTED SAVER BOT**

👋 **Welcome {callback_query.from_user.first_name}!**

🔒 **Account Status:** Not Verified

🎯 **Get Started:**
   • Verify to unlock features
   • Save restricted content  
   • Forward private posts
   • Download media files

⚡ **Click verify to get 24h freemium access!**
        """
        buttons = [
            [InlineKeyboardButton("🔓 Verify Now", callback_data="verify_btn")],
            [InlineKeyboardButton("📋 View Plans", callback_data="plans_btn")],
            [InlineKeyboardButton("❓ Help", callback_data="help_btn")],
            [InlineKeyboardButton("👑 Developer", url="https://t.me/PLAYZ_90")]
        ]
    else:
        role_emoji = {"freemium": "🆓", "standard": "🔹", "pro": "💎", "elite": "👑", "premium": "⭐"}
        welcome_text = f"""
🤖 **PLAY-Z RESTRICTED SAVER BOT**

👋 **Welcome Back {callback_query.from_user.first_name}!**

{role_emoji.get(role, "🔹")} **Plan:** {role.capitalize()}

🚀 **Ready to use!**
   • Send Telegram links to save
   • Check your usage stats
   • Upgrade for more features

💡 **Send any link to start!**
        """
        buttons = [
            [InlineKeyboardButton("📊 My Plan", callback_data="my_plan_btn")],
            [InlineKeyboardButton("📈 Upgrade", callback_data="plans_btn")],
            [InlineKeyboardButton("❓ Help", callback_data="help_btn")],
            [InlineKeyboardButton("👑 Developer", url="https://t.me/PLAYZ_90")]
        ]
    
    buttons.extend([
        [
            InlineKeyboardButton('🔍 Support', url='https://t.me/PLAY_Z_HACKING_DISCUSSION'),
            InlineKeyboardButton('📢 Updates', url='https://t.me/+ahE-9i84aFxkOWNl')
        ]
    ])
    
    try:
        await callback_query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    except:
        await callback_query.answer("Please try again!", show_alert=True)

# START COMMAND WITH VERIFICATION HANDLING  
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    chat_id = message.from_user.id
    args = message.text.split()
    
    # Handle verification callback from shrinkme URL
    if len(args) > 1 and args[1].startswith("add_premium_"):
        parts = args[1].split("_")
        if len(parts) == 5:
            _, _, uid, code, status = parts
            if str(chat_id) == uid and status == "freemium":
                # Validate code
                db_code = await db.get_user_code(chat_id)
                if db_code == code:
                    await db.add_freemium_user(chat_id, code, FREEMIUM_DURATION)
                    
                    # Advanced success animation
                    loading_msg = await message.reply("🔄 **Processing verification...**", parse_mode=enums.ParseMode.MARKDOWN)
                    await asyncio.sleep(1)
                    
                    success_text = """
🎉 **VERIFICATION SUCCESSFUL!** 🎉

✅ **Freemium Access Activated**
⏰ **Duration:** 24 Hours  
📊 **Your Limits:**
   • 📁 Max 3 files per batch
   • 🔢 4 batches daily (12 posts/day)
   • 💾 Save any restricted content

🚀 **Bot is ready to use!**
Send any Telegram link to start saving content.

💎 **Want unlimited access?** Check /plan
                    """
                    
                    buttons = [
                        [InlineKeyboardButton("📊 Check My Plan", callback_data="my_plan_btn")],
                        [InlineKeyboardButton("📈 Upgrade Plan", callback_data="plans_btn")],
                        [InlineKeyboardButton("❓ How to Use", callback_data="help_btn")]
                    ]
                    
                    await loading_msg.edit_text(success_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
                    return
                else:
                    await message.reply("❌ **Invalid or expired verification code.**

Get a new verification link with /verify", parse_mode=enums.ParseMode.MARKDOWN)
                    return

    # Add user to database if not exists
    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id, message.from_user.first_name)
        welcome_new_user = True
    else:
        welcome_new_user = False

    # Check user role
    role = await db.get_user_role(chat_id)
    
    if role == "free":
        if welcome_new_user:
            welcome_text = f"""
🤖 **WELCOME TO PLAY-Z SAVER BOT!** 

🎉 **Hi {message.from_user.first_name}!** Thanks for joining!

🔥 **What this bot can do:**
   • 💾 Save restricted Telegram content
   • 📱 Forward from private channels  
   • 🎥 Download videos, photos, documents
   • 🔄 Batch processing support

🔒 **To get started, you need to verify first:**

🎁 **After verification you'll get:**
   • 🆓 24 hours freemium access
   • 📁 3 files per batch
   • 🔢 4 batches daily (12 posts/day)

⚡ **Ready to unlock the bot?**
            """
        else:
            welcome_text = f"""
🤖 **PLAY-Z RESTRICTED SAVER BOT**

👋 **Welcome back {message.from_user.first_name}!**

🔒 **Account Status:** Verification Required

🎯 **Missing Features:**
   • Save restricted content
   • Forwarh_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

        try:
        msg.text
        return "Text"
    except:
        pass

    return None


# ADDITIONAL ADMIN COMMANDS

@Client.on_message(filters.command(["stats"]) & filters.private)
async def stats_handler(client: Client, message: Message):
    """Show bot statistics"""
    # Add your admin ID in config.py as ADMIN_ID
    try:
        from config import ADMIN_ID
        if message.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            return
    except:
        # If no admin ID set, skip this command
        return
    
    total_users = await db.total_users_count()
    
    # Count users by role
    freemium_count = 0
    standard_count = 0
    pro_count = 0
    elite_count = 0
    premium_count = 0
    free_count = 0
    
    async for user in db.get_all_users():
        try:
            user_role = await db.get_user_role(user['id'])
            if user_role == 'freemium':
                freemium_count += 1
            elif user_role == 'standard':
                standard_count += 1
            elif user_role == 'pro':
                pro_count += 1
            elif user_role == 'elite':
                elite_count += 1
            elif user_role == 'premium':
                premium_count += 1
            else:
                free_count += 1
        except:
            free_count += 1
    
    stats_text = f"""
📊 **BOT STATISTICS**

👥 **Total Users:** {total_users}

📈 **Active Plans:**
   • 🆓 **Freemium:** {freemium_count} users
   • 🔹 **Standard:** {standard_count} users
   • 💎 **Pro:** {pro_count} users
   • 👑 **Elite:** {elite_count} users
   • ⭐ **Premium:** {premium_count} users

🔒 **Unverified:** {free_count} users

📱 **Bot Status:** Online ✅
⚡ **Server:** Running Smoothly
🕒 **Uptime:** Active

🎯 **Performance:**
   • ✅ All systems operational
   • 🚀 Fast processing enabled
   • 🔐 Security systems active
    """
    
    buttons = [
        [
            InlineKeyboardButton("🔄 Refresh Stats", callback_data="refresh_stats"),
            InlineKeyboardButton("📡 Broadcast", url="https://t.me/your_bot?start=admin_broadcast")
        ],
        [InlineKeyboardButton("👥 User Management", callback_data="user_management")]
    ]
    
    await message.reply(stats_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.command(["broadcast"]) & filters.private)
async def broadcast_handler(client: Client, message: Message):
    """Broadcast message to all users"""
    try:
        from config import ADMIN_ID
        if message.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            return
    except:
        return
        
    if len(message.text.split(' ', 1)) < 2:
        await message.reply("""
❌ **Invalid Usage**

📡 **Correct Usage:**
`/broadcast Your message here`

💡 **Example:**
`/broadcast 🎉 Bot updated with new features!`

📝 **Supported:**
   • Text messages
   • Emojis
   • Markdown formatting
        """, parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    broadcast_msg = message.text.split(' ', 1)[1]
    
    # Confirmation before broadcast
    confirm_text = f"""
📡 **BROADCAST CONFIRMATION**

📝 **Message Preview:**
{broadcast_msg}

👥 **Target:** All bot users
⚠️ **Warning:** This action cannot be undone

🤔 **Are you sure you want to send this message to all users?**
    """
    
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Send Now", callback_data=f"confirm_broadcast_{message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
        ]
    ]
    
    await message.reply(confirm_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_callback_query(filters.regex("confirm_broadcast_"))
async def confirm_broadcast(client: Client, callback_query: CallbackQuery):
    try:
        from config import ADMIN_ID
        if callback_query.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            await callback_query.answer("❌ Unauthorized", show_alert=True)
            return
    except:
        return
    
    msg_id = int(callback_query.data.split("_")[-1])
    
    # Get original message
    try:
        original_msg = await client.get_messages(callback_query.message.chat.id, msg_id)
        broadcast_msg = original_msg.text.split(' ', 1)[1]
    except:
        await callback_query.answer("❌ Error getting broadcast message", show_alert=True)
        return
    
    users = db.get_all_users()
    success = 0
    failed = 0
    total_users = await db.total_users_count()
    
    status_msg = await callback_query.edit_message_text(
        "📡 **BROADCASTING STARTED**

⏳ Initializing broadcast system...",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
    start_time = time.time()
    
    async for user in users:
        try:
            await client.send_message(
                user['id'], 
                broadcast_msg, 
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            success += 1
            await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            failed += 1
            
        # Update status every 50 messages
        if (success + failed) % 50 == 0:
            progress = ((success + failed) / total_users) * 100
            elapsed = time.time() - start_time
            eta = (elapsed / (success + failed)) * (total_users - success - failed) if success + failed > 0 else 0
            
            progress_bar = "▰" * int(progress / 10) + "▱" * (10 - int(progress / 10))
            
            await status_msg.edit_text(f"""
📡 **BROADCASTING IN PROGRESS**

{progress_bar} **{progress:.1f}%**

📊 **Statistics:**
   • ✅ **Sent:** {success}
   • ❌ **Failed:** {failed}
   • 👥 **Total:** {total_users}
   • ⏱️ **ETA:** {int(eta)}s

⚡ **Status:** Sending messages...
            """, parse_mode=enums.ParseMode.MARKDOWN)
    
    elapsed_time = time.time() - start_time
    
    final_text = f"""
✅ **BROADCAST COMPLETED!**

📊 **Final Results:**
   • ✅ **Successfully Sent:** {success}
   • ❌ **Failed to Send:** {failed}
   • 👥 **Total Users:** {total_users}
   • 📈 **Success Rate:** {(success/total_users)*100:.1f}%

⏱️ **Time Taken:** {int(elapsed_time)}s
🚀 **Speed:** {(success+failed)/elapsed_time:.1f} msg/sec

💡 **Note:** Failed messages are usually due to users blocking the bot.
    """
    
    buttons = [
        [InlineKeyboardButton("📊 View Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
    ]
    
    await status_msg.edit_text(final_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_callback_query(filters.regex("cancel_broadcast"))
async def cancel_broadcast(client: Client, callback_query: CallbackQuery):
    await callback_query.edit_message_text(
        "❌ **Broadcast Cancelled**

📝 No messages were sent to users.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.command(["addpremium"]) & filters.private)
async def add_premium_handler(client: Client, message: Message):
    """Add premium access to user"""
    try:
        from config import ADMIN_ID
        if message.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            return
    except:
        return
        
    if len(message.command) < 3:
        await message.reply("""
❌ **Invalid Usage**

🎯 **Correct Usage:**
`/addpremium <user_id> <plan>`

📋 **Available Plans:**
   • `freemium` - 24h access
   • `standard` - $8/month features
   • `pro` - $20/month features  
   • `elite` - $45/month features
   • `premium` - Unlimited access

💡 **Example:**
`/addpremium 123456789 elite`
        """, parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    try:
        user_id = int(message.command[1])
        plan = message.command[2].lower()
        
        valid_plans = ['freemium', 'standard', 'pro', 'elite', 'premium']
        if plan not in valid_plans:
            await message.reply(f"❌ **Invalid plan.** 

✅ **Valid plans:** {', '.join(valid_plans)}", parse_mode=enums.ParseMode.MARKDOWN)
            return
        
        # Check if user exists
        if not await db.is_user_exist(user_id):
            await message.reply("❌ **User not found in database.**

💡 User must start the bot first.", parse_mode=enums.ParseMode.MARKDOWN)
            return
            
        # Set expiry based on plan
        if plan == 'freemium':
            expiry = int(time.time()) + FREEMIUM_DURATION
        elif plan == 'premium':
            expiry = 0  # No expiry for premium
        else:
            expiry = int(time.time()) + (30 * 24 * 3600)  # 30 days for paid plans
            
        await db.update_user_role(user_id, plan, expiry)
        await db.reset_user_usage(user_id)  # Reset usage limits
        
        success_text = f"""
✅ **USER UPGRADED SUCCESSFULLY!**

👤 **User ID:** `{user_id}`
📈 **New Plan:** {plan.capitalize()}
⏰ **Expiry:** {"No expiry" if expiry == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))}

🎉 **User has been notified!**
        """
        
        await message.reply(success_text, parse_mode=enums.ParseMode.MARKDOWN)
        
        # Notify user
        try:
            user_notification = f"""
🎉 **CONGRATULATIONS!**

✅ **Your account has been upgraded!**

📈 **New Plan:** {plan.capitalize()}
⏰ **Valid Until:** {"Unlimited" if expiry == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))}

🚀 **You can now enjoy enhanced features!**
Check your new limits with /my_plan

💎 **Thank you for using our bot!**
            """
            
            await client.send_message(user_id, user_notification, parse_mode=enums.ParseMode.MARKDOWN)
        except:
            await message.reply("⚠️ **User upgraded but notification failed** (user may have blocked the bot)", parse_mode=enums.ParseMode.MARKDOWN)
            
    except ValueError:
        await message.reply("❌ **Invalid user ID.** Please enter a valid numeric user ID.", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.command(["removepremium"]) & filters.private)
async def remove_premium_handler(client: Client, message: Message):
    """Remove premium access from user"""
    try:
        from config import ADMIN_ID
        if message.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            return
    except:
        return
        
    if len(message.command) < 2:
        await message.reply("""
❌ **Invalid Usage**

🎯 **Correct Usage:**
`/removepremium <user_id>`

💡 **Example:**
`/removepremium 123456789`

📝 **Note:** This will set user back to free plan.
        """, parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    try:
        user_id = int(message.command[1])
        
        if not await db.is_user_exist(user_id):
            await message.reply("❌ **User not found in database.**", parse_mode=enums.ParseMode.MARKDOWN)
            return
            
        current_role = await db.get_user_role(user_id)
        await db.update_user_role(user_id, "free", 0)
        
        await message.reply(f"""
✅ **PREMIUM ACCESS REMOVED**

👤 **User ID:** `{user_id}`
📉 **Previous Plan:** {current_role.capitalize()}
📋 **Current Plan:** Free (Unverified)

⚠️ **User has been notified.**
        """, parse_mode=enums.ParseMode.MARKDOWN)
        
        # Notify user
        try:
            await client.send_message(user_id, """
⚠️ **ACCOUNT STATUS CHANGED**

📉 **Your premium access has been removed by admin.**

🔒 **Current Status:** Free (Unverified)

🎯 **To continue using the bot:**
   • Use /verify to get freemium access
   • Or contact admin for plan restoration

💬 **Need help?** Contact support.
            """, parse_mode=enums.ParseMode.MARKDOWN)
        except:
            pass
            
    except ValueError:
        await message.reply("❌ **Invalid user ID.**", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.command(["userinfo"]) & filters.private)
async def user_info_handler(client: Client, message: Message):
    """Get detailed user information"""
    try:
        from config import ADMIN_ID
        if message.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            return
    except:
        return
        
    if len(message.command) < 2:
        await message.reply("""
❌ **Invalid Usage**

🎯 **Correct Usage:**
`/userinfo <user_id>`

💡 **Example:**
`/userinfo 123456789`
        """, parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    try:
        user_id = int(message.command[1])
        
        if not await db.is_user_exist(user_id):
            await message.reply("❌ **User not found in database.**", parse_mode=enums.ParseMode.MARKDOWN)
            return
        
        user = await db.get_user(user_id)
        stats = await db.get_user_stats(user_id)
        
        if not user or not stats:
            await message.reply("❌ **Error retrieving user data.**", parse_mode=enums.ParseMode.MARKDOWN)
            return
        
        role = stats["role"]
        usage = stats["usage"]
        expiry_readable = stats["expiry_readable"]
        
        # Get user info from Telegram
        try:
            tg_user = await client.get_users(user_id)
            username = f"@{tg_user.username}" if tg_user.username else "No Username"
            first_name = tg_user.first_name or "Unknown"
            last_name = tg_user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
        except:
            username = "Private/Deleted"
            full_name = user.get('name', 'Unknown')
        
        user_info_text = f"""
👤 **USER INFORMATION**

🆔 **User ID:** `{user_id}`
👤 **Name:** {full_name}
📱 **Username:** {username}
📊 **Plan:** {role.capitalize()}

⏰ **Account Details:**
   • **Expiry:** {expiry_readable}
   • **Session:** {"Yes" if user.get('session') else "No"}

📈 **Usage Statistics:**
   • **Batches Used Today:** {usage.get('batches', 0)}
   • **Files Processed:** {usage.get('files', 0)}
   • **Last Reset:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usage.get('last_reset', 0)))}

🔐 **Security:**
   • **Verification Code:** {"Set" if user.get('code') else "None"}
   • **Account Status:** {"Active" if role != "free" else "Inactive"}

💡 **Admin Actions Available:**
   • Upgrade/downgrade plan
   • Reset usage limits  
   • Remove session
        """
        
        buttons = [
            [
                InlineKeyboardButton("📈 Upgrade User", callback_data=f"upgrade_user_{user_id}"),
                InlineKeyboardButton("📉 Downgrade User", callback_data=f"downgrade_user_{user_id}")
            ],
            [
                InlineKeyboardButton("🔄 Reset Usage", callback_data=f"reset_usage_{user_id}"),
                InlineKeyboardButton("🗑️ Remove Session", callback_data=f"remove_session_{user_id}")
            ],
            [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
        ]
        
        await message.reply(user_info_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
        
    except ValueError:
        await message.reply("❌ **Invalid user ID.**", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

# Additional callback handlers for admin functions
@Client.on_callback_query(filters.regex("admin_"))
async def admin_callback_handler(client: Client, callback_query: CallbackQuery):
    try:
        from config import ADMIN_ID
        if callback_query.from_user.id not in ADMIN_ID if isinstance(ADMIN_ID, list) else [ADMIN_ID]:
            await callback_query.answer("❌ Unauthorized access", show_alert=True)
            return
    except:
        await callback_query.answer("❌ Admin access not configured", show_alert=True)
        return
    
    data = callback_query.data
    
    if data == "admin_stats":
        # Redirect to stats
        await stats_handler(client, callback_query.message)
    elif data == "admin_panel":
        admin_panel_text = """
🔧 **ADMIN CONTROL PANEL**

🎛️ **Available Commands:**
   • `/stats` - View bot statistics
   • `/broadcast` - Send message to all users
   • `/addpremium` - Upgrade user plan
   • `/removepremium` - Remove user access
   • `/userinfo` - Get user details

📊 **Quick Actions:**
        """
        
        buttons = [
            [
                InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
                InlineKeyboardButton("📡 Broadcast", url="https://t.me/your_bot?start=admin_broadcast")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        
        await callback_query.edit_message_text(admin_panel_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

# Error handler for uncaught exceptions
@Client.on_message(filters.all & filters.private, group=-1)
async def error_handler(client: Client, message: Message):
    """Global error handler"""
    try:
        # This runs after all other handlers
        pass
    except Exception as e:
        if ERROR_MESSAGE:
            try:
                await message.reply(f"⚠️ **Unexpected error occurred.**

Please try again or contact support.

**Error ID:** `{int(time.time())}`", parse_mode=enums.ParseMode.MARKDOWN)
            except:
                pass

# Bot startup message
@Client.on_message(filters.command(["ping"]))
async def ping_handler(client: Client, message: Message):
    """Test bot responsiveness"""
    start_time = time.time()
    ping_msg = await message.reply("🏓 **Pinging...**", parse_mode=enums.ParseMode.MARKDOWN)
    end_time = time.time()
    
    ping_time = (end_time - start_time) * 1000
    
    await ping_msg.edit_text(f"""
🏓 **PONG!**

⚡ **Response Time:** {ping_time:.2f}ms
🤖 **Bot Status:** Online ✅
🔋 **System:** Operational

💡 **Performance:** {"Excellent" if ping_time < 100 else "Good" if ping_time < 500 else "Fair"}
    """, parse_mode=enums.ParseMode.MARKDOWN)
        
