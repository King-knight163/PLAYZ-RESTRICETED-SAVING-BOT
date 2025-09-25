# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
import asyncio
import time
import re
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, enums
from asyncio.exceptions import TimeoutError
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
    UserDeactivated,
    AuthKeyUnregistered
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

# Session management tracking
login_sessions = {}

def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove spaces and special characters
    clean_phone = re.sub(r'[^d+]', '', phone)
    
    # Check if it starts with + and has country code
    if not clean_phone.startswith('+'):
        return False, "Phone number must start with country code (e.g., +1, +91)"
    
    # Check length (should be between 10-15 digits including country code)
    if len(clean_phone) < 8 or len(clean_phone) > 16:
        return False, "Phone number length is invalid"
    
    return True, clean_phone

async def check_session_validity(session_string):
    """Check if session string is valid and working"""
    try:
        test_client = Client(":memory:", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await test_client.connect()
        me = await test_client.get_me()
        await test_client.disconnect()
        return True, me
    except Exception as e:
        return False, str(e)

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def enhanced_logout(client, message):
    """Enhanced logout with confirmation and session cleanup"""
    user_data = await db.get_session(message.from_user.id)
    
    if user_data is None:
        await message.reply(
            "❌ **No Active Session Found**

🔍 You are not currently logged in.
Use /login to create a new session.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    # Show confirmation with session info
    try:
        # Test current session
        is_valid, session_info = await check_session_validity(user_data)
        
        if is_valid:
            session_status = f"✅ **Active Session**
👤 **Account:** {session_info.first_name}"
        else:
            session_status = "⚠️ **Session Already Expired**
Will cleanup database entry."
    except:
        session_status = "🔍 **Checking session...**"
    
    logout_text = f"""
🚪 **LOGOUT CONFIRMATION**

{session_status}

⚠️ **Warning:** Logging out will:
   • Remove your session from bot database
   • Stop access to restricted content
   • Require re-login for future use

🤔 **Are you sure you want to logout?**
    """
    
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Logout", callback_data=f"confirm_logout_{message.from_user.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_logout")
        ],
        [InlineKeyboardButton("🔄 Check Session Status", callback_data=f"check_session_{message.from_user.id}")]
    ]
    
    await message.reply(
        logout_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("confirm_logout_"))
async def confirm_logout(client, callback_query):
    """Execute logout after confirmation"""
    user_id = int(callback_query.data.split("_")[-1])
    
    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Unauthorized action!", show_alert=True)
        return
    
    # Remove session from database
    await db.set_session(user_id, session=None)
    
    # Clean up any login session data
    if user_id in login_sessions:
        del login_sessions[user_id]
    
    success_text = """
✅ **LOGOUT SUCCESSFUL**

🚪 **Session Removed:** Your account has been logged out
🔒 **Database Cleaned:** All session data removed
🛡️ **Security:** Your privacy is protected

💡 **To use restricted content features again:**
Use /login to create a new session

🆔 **Your user preferences and plan remain active**
    """
    
    await callback_query.edit_message_text(
        success_text,
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("cancel_logout"))
async def cancel_logout(client, callback_query):
    """Cancel logout operation"""
    await callback_query.edit_message_text(
        "❌ **Logout Cancelled**

🔐 Your session remains active.
You can continue using the bot normally.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("check_session_"))
async def check_session_status(client, callback_query):
    """Check current session status"""
    user_id = int(callback_query.data.split("_")[-1])
    
    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    user_data = await db.get_session(user_id)
    
    if not user_data:
        status_text = "❌ **No Session Found**

You are not logged in."
    else:
        is_valid, info = await check_session_validity(user_data)
        
        if is_valid:
            status_text = f"""
✅ **Session Active & Valid**

👤 **Account Info:**
   • **Name:** {info.first_name} {info.last_name or ''}
   • **Username:** @{info.username or 'None'}
   • **Phone:** {info.phone_number or 'Hidden'}
   • **ID:** `{info.id}`

🔒 **Session Status:** Working properly
⚡ **Connection:** Stable
            """
        else:
            status_text = f"""
❌ **Session Expired/Invalid**

⚠️ **Error:** {info[:100]}

🔄 **Recommendation:**
   • Logout current session
   • Login again with /login
   • Check your Telegram account status
            """
    
    await callback_query.edit_message_text(
        status_text,
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def enhanced_login(bot: Client, message: Message):
    """Enhanced login with better UX and error handling"""
    user_id = message.from_user.id
    
    # Check if already logged in
    user_data = await db.get_session(user_id)
    if user_data is not None:
        is_valid, session_info = await check_session_validity(user_data)
        
        if is_valid:
            buttons = [
                [InlineKeyboardButton("🚪 Logout & Re-login", callback_data=f"force_logout_{user_id}")],
                [InlineKeyboardButton("✅ Keep Current Session", callback_data="keep_session")]
            ]
            
            await message.reply(
                f"✅ **Already Logged In**

👤 **Current Account:** {session_info.first_name}
🔐 **Session Status:** Active

🤔 **What would you like to do?**",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        else:
            # Session expired, auto-cleanup
            await db.set_session(user_id, session=None)
    
    # Check user plan before allowing login
    user_role = await db.get_user_role(user_id)
    if user_role == "free":
        await message.reply(
            "🔒 **Verification Required**

You need to verify your account first before logging in.

Use /verify to get freemium access, then try /login again.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    # Start login process
    login_sessions[user_id] = {
        "step": "phone",
        "start_time": time.time(),
        "attempts": 0
    }
    
    welcome_text = """
🔐 **TELEGRAM LOGIN PROCESS**

🎯 **Purpose:** Access restricted content from private channels

⚠️ **Important Notes:**
   • Your session is stored securely
   • No passwords are saved
   • Session can be revoked anytime
   • Only works with your own Telegram account

📱 **Step 1:** Phone Number Required

💡 **Format Examples:**
   • USA: `+1 234 567 8901`
   • India: `+91 98765 43210`
   • UK: `+44 20 1234 5678`

🚫 **Type /cancel to stop the process**
    """
    
    await message.reply(welcome_text, parse_mode=enums.ParseMode.MARKDOWN)
    
    # Get phone number with validation
    phone_number_msg = await bot.ask(
        chat_id=user_id, 
        text="📞 **Enter your phone number with country code:**

💡 Example: `+1234567890`",
        timeout=300
    )
    
    if phone_number_msg.text == '/cancel':
        del login_sessions[user_id]
        return await phone_number_msg.reply('❌ **Login process cancelled!**', parse_mode=enums.ParseMode.MARKDOWN)
    
    # Validate phone number
    is_valid, phone_result = validate_phone_number(phone_number_msg.text)
    if not is_valid:
        del login_sessions[user_id]
        return await phone_number_msg.reply(f'❌ **Invalid phone number:** {phone_result}', parse_mode=enums.ParseMode.MARKDOWN)
    
    phone_number = phone_result
    login_sessions[user_id]["phone"] = phone_number
    login_sessions[user_id]["step"] = "otp"
    
    # Initialize client and send OTP
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    
    otp_status = await phone_number_msg.reply("📤 **Sending OTP...**

⏳ Please wait...", parse_mode=enums.ParseMode.MARKDOWN)
    
    try:
        code = await client.send_code(phone_number)
        login_sessions[user_id]["code_hash"] = code.phone_code_hash
        login_sessions[user_id]["client"] = client
        
        await otp_status.edit_text(
            "✅ **OTP Sent Successfully!**

📱 Check your Telegram app for the verification code.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        otp_text = """
📲 **OTP VERIFICATION**

🔍 **Check your official Telegram app for the verification code**

📝 **Format Instructions:**
   • If OTP is `12345`, send it as: `1 2 3 4 5`
   • Add spaces between each digit
   • Don't include any other characters

⏰ **Timeout:** 10 minutes
🚫 **Cancel:** Type /cancel
        """
        
        phone_code_msg = await bot.ask(
            user_id, 
            otp_text,
            filters=filters.text, 
            timeout=600,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except PhoneNumberInvalid:
        await client.disconnect()
        del login_sessions[user_id]
        return await otp_status.edit_text('❌ **Phone number is invalid.**

Please check and try again with /login', parse_mode=enums.ParseMode.MARKDOWN)
    except FloodWait as e:
        await client.disconnect()
        del login_sessions[user_id]
        return await otp_status.edit_text(f'⏳ **Rate limited.**

Please wait {e.value} seconds and try again.', parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await client.disconnect()
        del login_sessions[user_id]
        return await otp_status.edit_text(f'❌ **Error sending OTP:**
`{str(e)[:100]}`', parse_mode=enums.ParseMode.MARKDOWN)
    
    if phone_code_msg.text == '/cancel':
        await client.disconnect()
        del login_sessions[user_id]
        return await phone_code_msg.reply('❌ **Login process cancelled!**', parse_mode=enums.ParseMode.MARKDOWN)
    
    # Verify OTP
    login_sessions[user_id]["step"] = "verifying"
    verify_status = await phone_code_msg.reply("🔄 **Verifying OTP...**", parse_mode=enums.ParseMode.MARKDOWN)
    
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        login_sessions[user_id]["step"] = "success"
        
    except PhoneCodeInvalid:
        await client.disconnect()
        del login_sessions[user_id]
        return await verify_status.edit_text('❌ **Invalid OTP.**

Please try /login again with correct OTP.', parse_mode=enums.ParseMode.MARKDOWN)
    except PhoneCodeExpired:
        await client.disconnect()
        del login_sessions[user_id]
        return await verify_status.edit_text('⌛ **OTP expired.**

Please try /login again to get a new OTP.', parse_mode=enums.ParseMode.MARKDOWN)
    except SessionPasswordNeeded:
        login_sessions[user_id]["step"] = "2fa"
        await verify_status.edit_text("🔐 **Two-Factor Authentication detected.**

Processing...", parse_mode=enums.ParseMode.MARKDOWN)
        
        two_fa_text = """
🔐 **TWO-FACTOR AUTHENTICATION**

🔑 **Your account has 2FA enabled (Cloud Password)**

🛡️ **Security Notice:**
   • This is your Telegram cloud password
   • Not your phone lock password
   • Set up in: Settings > Privacy & Security > Two-Step Verification

📝 **Enter your cloud password:**

⏰ **Timeout:** 5 minutes
🚫 **Cancel:** Type /cancel
        """
        
        two_step_msg = await bot.ask(
            user_id, 
            two_fa_text,
            filters=filters.text, 
            timeout=300,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        if two_step_msg.text == '/cancel':
            await client.disconnect()
            del login_sessions[user_id]
            return await two_step_msg.reply('❌ **Login process cancelled!**', parse_mode=enums.ParseMode.MARKDOWN)
        
        password_status = await two_step_msg.reply("🔐 **Verifying password...**", parse_mode=enums.ParseMode.MARKDOWN)
        
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
            login_sessions[user_id]["step"] = "success"
            await password_status.edit_text("✅ **Password verified!**", parse_mode=enums.ParseMode.MARKDOWN)
        except PasswordHashInvalid:
            await client.disconnect()
            del login_sessions[user_id]
            return await password_status.edit_text('❌ **Invalid password.**

Please try /login again with correct password.', parse_mode=enums.ParseMode.MARKDOWN)
    
    # Generate session string
    session_generation_status = await bot.send_message(user_id, "🔄 **Generating secure session...**", parse_mode=enums.ParseMode.MARKDOWN)
    
    try:
        string_session = await client.export_session_string()
        await client.disconnect()
        
        if len(string_session) < SESSION_STRING_SIZE:
            del login_sessions[user_id]
            return await session_generation_status.edit_text('❌ **Invalid session generated.**

Please try /login again.', parse_mode=enums.ParseMode.MARKDOWN)
        
        # Test the session
        is_valid, user_info = await check_session_validity(string_session)
        if not is_valid:
            del login_sessions[user_id]
            return await session_generation_status.edit_text(f'❌ **Session validation failed:**
`{user_info[:100]}`', parse_mode=enums.ParseMode.MARKDOWN)
        
        # Save to database
        await db.set_session(user_id, session=string_session)
        
        # Success message
        success_text = f"""
🎉 **LOGIN SUCCESSFUL!**

✅ **Account Connected:** {user_info.first_name}
🔐 **Session:** Securely stored
⚡ **Status:** Ready to use

🚀 **You can now:**
   • Access restricted content
   • Forward from private channels  
   • Save media files
   • Use all bot features

💡 **Pro Tips:**
   • Use /logout to remove session anytime
   • Session expires if your Telegram account changes
   • Keep your account active for best performance

🎯 **Start saving content by sending any Telegram link!**
        """
        
        buttons = [
            [InlineKeyboardButton("📊 Check My Plan", callback_data="my_plan_btn")],
            [InlineKeyboardButton("❓ How to Use", callback_data="help_btn")]
        ]
        
        await session_generation_status.edit_text(
            success_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        # Cleanup
        if user_id in login_sessions:
            del login_sessions[user_id]
            
    except Exception as e:
        await client.disconnect()
        if user_id in login_sessions:
            del login_sessions[user_id]
        return await session_generation_status.edit_text(f"❌ **Login error:**
`{str(e)[:150]}`

Try /login again.", parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_callback_query(filters.regex("force_logout_"))
async def force_logout(client, callback_query):
    """Force logout for re-login"""
    user_id = int(callback_query.data.split("_")[-1])
    
    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    await db.set_session(user_id, session=None)
    await callback_query.edit_message_text(
        "✅ **Session removed successfully!**

Now use /login to create a new session.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("keep_session"))
async def keep_current_session(client, callback_query):
    """Keep current session"""
    await callback_query.edit_message_text(
        "✅ **Current session maintained.**

You can continue using the bot normally.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Session health check command
@Client.on_message(filters.command("session") & filters.private)
async def session_info(client, message):
    """Check session health and info"""
    user_id = message.from_user.id
    user_data = await db.get_session(user_id)
    
    if not user_data:
        await message.reply(
            "❌ **No Session Found**

You are not logged in. Use /login to create a session.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    checking_msg = await message.reply("🔍 **Checking session health...**", parse_mode=enums.ParseMode.MARKDOWN)
    
    is_valid, info = await check_session_validity(user_data)
    
    if is_valid:
        session_text = f"""
✅ **SESSION HEALTH: EXCELLENT**

👤 **Account Information:**
   • **Name:** {info.first_name} {info.last_name or ''}
   • **Username:** @{info.username or 'None'}
   • **Phone:** {info.phone_number or 'Hidden'}
   • **Account ID:** `{info.id}`

🔒 **Session Status:**
   • **Connection:** Active ✅
   • **Authentication:** Valid ✅
   • **Permissions:** Full Access ✅

🎯 **Available Actions:**
   • Access restricted content
   • Download from private channels
   • Save all media types

🛠️ **Management:**
   • Use /logout to remove session
   • Session auto-expires if account changes
        """
        
        buttons = [
            [InlineKeyboardButton("🚪 Logout Session", callback_data=f"confirm_logout_{user_id}")],
            [InlineKeyboardButton("🔄 Refresh Status", callback_data=f"check_session_{user_id}")]
        ]
    else:
        session_text = f"""
❌ **SESSION HEALTH: EXPIRED/INVALID**

🚨 **Issues Detected:**
   • **Status:** Not working
   • **Error:** {info[:150]}

🔧 **Recommended Actions:**
   1. Logout current session with /logout
   2. Create new session with /login
   3. Ensure your Telegram account is active

⚠️ **Common Causes:**
   • Account password changed
   • 2FA settings modified
   • Account deactivated temporarily
   • Session too old
        """
        
        buttons = [
            [InlineKeyboardButton("🔄 Re-login", callback_data=f"force_logout_{user_id}")],
            [InlineKeyboardButton("🚪 Clear Session", callback_data=f"confirm_logout_{user_id}")]
        ]
    
    await checking_msg.edit_text(
        session_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Cleanup function for expired login sessions
@Client.on_message(filters.command("cleanup") & filters.private)
async def cleanup_expired_sessions(client, message):
    """Admin function to cleanup expired login attempts"""
    current_time = time.time()
    expired_sessions = []
    
    for user_id, session_data in login_sessions.items():
        if current_time - session_data.get("start_time", 0) > 1800:  # 30 minutes
            expired_sessions.append(user_id)
    
    for user_id in expired_sessions:
        if user_id in login_sessions:
            try:
                client_obj = login_sessions[user_id].get("client")
                if client_obj:
                    await client_obj.disconnect()
            except:
                pass
            del login_sessions[user_id]
    
    if expired_sessions:
        await message.reply(f"🧹 **Cleaned up {len(expired_sessions)} expired login sessions.**", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply("✅ **No expired sessions found.**", parse_mode=enums.ParseMode.MARKDOWN)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
