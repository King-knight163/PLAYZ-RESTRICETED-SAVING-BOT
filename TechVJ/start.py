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
        
