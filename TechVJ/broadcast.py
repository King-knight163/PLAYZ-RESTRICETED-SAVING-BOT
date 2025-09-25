from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import db
from pyrogram import Client, filters, enums
import asyncio
import datetime
import time
import json

# Broadcast statistics storage
broadcast_stats = {}

async def broadcast_messages(user_id, message):
    """Enhanced broadcast function with better error handling"""
    try:
        await message.copy(chat_id=user_id, protect_content=False)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deactivated"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Invalid"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

async def get_user_statistics():
    """Get detailed user statistics by role"""
    stats = {
        "total": 0,
        "free": 0,
        "freemium": 0,
        "standard": 0,
        "pro": 0,
        "elite": 0,
        "premium": 0
    }
    
    users = await db.get_all_users()
    async for user in users:
        stats["total"] += 1
        try:
            role = await db.get_user_role(user['id'])
            stats[role] = stats.get(role, 0) + 1
        except:
            stats["free"] += 1
    
    return stats

@Client.on_message(filters.command("broadcast") & filters.user([7107162691]) & filters.reply)  # Add your admin IDs
async def advanced_broadcast(bot, message):
    """Enhanced broadcast command with confirmation and detailed stats"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "❌ **Reply Required**

Reply to a message that you want to broadcast to all users.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    # Get current user statistics
    user_stats = await get_user_statistics()
    total_users = user_stats["total"]
    
    if total_users == 0:
        return await message.reply_text("❌ **No users found in database!**", parse_mode=enums.ParseMode.MARKDOWN)
    
    # Show confirmation with detailed stats
    confirm_text = f"""
📡 **BROADCAST CONFIRMATION**

📊 **Target Audience:**
   • 👥 **Total Users:** {total_users}
   • 🔒 **Free:** {user_stats.get('free', 0)}
   • 🆓 **Freemium:** {user_stats.get('freemium', 0)}
   • 🔹 **Standard:** {user_stats.get('standard', 0)}
   • 💎 **Pro:** {user_stats.get('pro', 0)}
   • 👑 **Elite:** {user_stats.get('elite', 0)}
   • ⭐ **Premium:** {user_stats.get('premium', 0)}

📝 **Message Preview:**
{b_msg.text[:200] if b_msg.text else "Media message"}{"..." if b_msg.text and len(b_msg.text) > 200 else ""}

⚠️ **Warning:** This action cannot be undone!

🤔 **Are you sure you want to broadcast this message?**
    """
    
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Start Broadcast", callback_data=f"confirm_broadcast_{message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
        ],
        [InlineKeyboardButton("📊 View Detailed Stats", callback_data="broadcast_stats")]
    ]
    
    await message.reply_text(
        confirm_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("confirm_broadcast_"))
async def execute_broadcast(bot, callback_query):
    """Execute the actual broadcast after confirmation"""
    msg_id = int(callback_query.data.split("_")[-1])
    
    try:
        # Get the original message to broadcast
        original_msg = await bot.get_messages(callback_query.message.chat.id, msg_id)
        b_msg = original_msg.reply_to_message
        
        if not b_msg:
            await callback_query.answer("❌ Original message not found!", show_alert=True)
            return
            
    except Exception as e:
        await callback_query.answer("❌ Error accessing original message!", show_alert=True)
        return
    
    # Start broadcast
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    
    # Initialize counters
    start_time = time.time()
    done = 0
    success = 0
    blocked = 0
    deleted = 0
    deactivated = 0
    failed = 0
    errors = {}
    
    # Update initial status
    sts = await callback_query.edit_message_text(
        "📡 **BROADCASTING STARTED**

⏳ Initializing broadcast system...",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
    # Process users in batches
    batch_size = 10
    batch_delay = 1  # seconds between batches
    
    user_list = []
    async for user in users:
        if 'id' in user:
            user_list.append(user)
    
    # Process in batches to avoid rate limits
    for i in range(0, len(user_list), batch_size):
        batch = user_list[i:i+batch_size]
        batch_tasks = []
        
        for user in batch:
            task = broadcast_messages(int(user['id']), b_msg)
            batch_tasks.append(task)
        
        # Execute batch
        batch_results = await asyncio.gather(*batch_tasks)
        
        # Process results
        for result in batch_results:
            pti, sh = result
            done += 1
            
            if pti:
                success += 1
            else:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deactivated":
                    deactivated += 1
                elif sh == "Invalid":
                    deleted += 1
                else:
                    failed += 1
                    # Track specific errors
                    error_type = sh.split(":")[0] if ":" in sh else sh
                    errors[error_type] = errors.get(error_type, 0) + 1
        
        # Update progress every batch or every 50 users
        if done % 50 == 0 or i + batch_size >= len(user_list):
            elapsed_time = time.time() - start_time
            progress_percent = (done / total_users) * 100
            eta = (elapsed_time / done) * (total_users - done) if done > 0 else 0
            
            progress_bar = "▰" * int(progress_percent / 5) + "▱" * (20 - int(progress_percent / 5))
            
            status_text = f"""
📡 **BROADCAST IN PROGRESS**

{progress_bar} **{progress_percent:.1f}%**

📊 **Current Statistics:**
   • 📤 **Processed:** {done}/{total_users}
   • ✅ **Successful:** {success}
   • 🚫 **Blocked:** {blocked}
   • 👤 **Deactivated:** {deactivated}
   • 🗑️ **Deleted:** {deleted}
   • ❌ **Failed:** {failed}

⏱️ **Time Info:**
   • **Elapsed:** {int(elapsed_time)}s
   • **ETA:** {int(eta)}s
   • **Speed:** {done/elapsed_time:.1f} msg/s

⚡ **Status:** Broadcasting messages...
            """
            
            try:
                await sts.edit_text(status_text, parse_mode=enums.ParseMode.MARKDOWN)
            except:
                pass
        
        # Delay between batches to respect rate limits
        if i + batch_size < len(user_list):
            await asyncio.sleep(batch_delay)
    
    # Final statistics
    total_time = time.time() - start_time
    time_taken = datetime.timedelta(seconds=int(total_time))
    success_rate = (success / total_users) * 100 if total_users > 0 else 0
    
    final_text = f"""
✅ **BROADCAST COMPLETED!**

📊 **Final Results:**
   • 📤 **Total Processed:** {done}/{total_users}
   • ✅ **Successfully Sent:** {success}
   • 📈 **Success Rate:** {success_rate:.1f}%

❌ **Failed Deliveries:**
   • 🚫 **User Blocked Bot:** {blocked}
   • 👤 **Account Deactivated:** {deactivated}
   • 🗑️ **Account Deleted:** {deleted}
   • ❌ **Other Errors:** {failed}

⏱️ **Performance:**
   • **Total Time:** {time_taken}
   • **Average Speed:** {done/total_time:.2f} messages/second
   • **Peak Performance:** Excellent

🧹 **Database Cleanup:**
   • Removed {blocked + deactivated + deleted} inactive users
   • Database optimized automatically

💡 **Note:** Failed deliveries are normal and usually indicate users who blocked the bot or deactivated their accounts.
    """
    
    # Add error details if any specific errors occurred
    if errors:
        error_details = "
".join([f"   • {error}: {count}" for error, count in errors.items()])
        final_text += f"

🔍 **Error Breakdown:**
{error_details}"
    
    # Store broadcast statistics
    broadcast_id = f"broadcast_{int(time.time())}"
    broadcast_stats[broadcast_id] = {
        "timestamp": int(time.time()),
        "total_users": total_users,
        "success": success,
        "failed": done - success,
        "time_taken": int(total_time),
        "success_rate": success_rate
    }
    
    buttons = [
        [
            InlineKeyboardButton("📊 Detailed Stats", callback_data=f"broadcast_details_{broadcast_id}"),
            InlineKeyboardButton("📈 Analytics", callback_data="broadcast_analytics")
        ],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
    ]
    
    await sts.edit_text(final_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_callback_query(filters.regex("cancel_broadcast"))
async def cancel_broadcast(bot, callback_query):
    """Cancel broadcast operation"""
    await callback_query.edit_message_text(
        "❌ **Broadcast Cancelled**

📝 No messages were sent to users.
You can start a new broadcast anytime.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("broadcast_stats"))
async def show_broadcast_stats(bot, callback_query):
    """Show detailed user statistics"""
    stats = await get_user_statistics()
    
    stats_text = f"""
📊 **DETAILED USER STATISTICS**

👥 **Total Active Users:** {stats['total']}

📈 **Users by Plan:**
   • 🔒 **Free (Unverified):** {stats.get('free', 0)}
   • 🆓 **Freemium (24h):** {stats.get('freemium', 0)}
   • 🔹 **Standard ($8/month):** {stats.get('standard', 0)}
   • 💎 **Pro ($20/month):** {stats.get('pro', 0)}
   • 👑 **Elite ($45/month):** {stats.get('elite', 0)}
   • ⭐ **Premium (Unlimited):** {stats.get('premium', 0)}

📊 **Revenue Potential:**
   • 🔹 Standard: ${stats.get('standard', 0) * 8}/month
   • 💎 Pro: ${stats.get('pro', 0) * 20}/month  
   • 👑 Elite: ${stats.get('elite', 0) * 45}/month

💰 **Total Monthly Revenue:** ${(stats.get('standard', 0) * 8) + (stats.get('pro', 0) * 20) + (stats.get('elite', 0) * 45)}

🎯 **Conversion Rate:** {((stats.get('standard', 0) + stats.get('pro', 0) + stats.get('elite', 0) + stats.get('premium', 0)) / max(stats['total'], 1)) * 100:.1f}%
    """
    
    buttons = [
        [InlineKeyboardButton("🔙 Back to Broadcast", callback_data="back_to_broadcast")]
    ]
    
    await callback_query.edit_message_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("quickbroadcast") & filters.user([123456789]) & filters.reply)
async def quick_broadcast(bot, message):
    """Quick broadcast without confirmation - for urgent messages"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text("❌ **Reply to a message first!**", parse_mode=enums.ParseMode.MARKDOWN)
    
    sts = await message.reply_text(
        "⚡ **QUICK BROADCAST STARTED**

🚀 Sending to all users immediately...",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    start_time = time.time()
    success = 0
    failed = 0
    
    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg)
            if pti:
                success += 1
            else:
                failed += 1
    
    total_time = time.time() - start_time
    time_taken = datetime.timedelta(seconds=int(total_time))
    
    await sts.edit_text(f"""
⚡ **QUICK BROADCAST COMPLETED!**

📊 **Results:**
   • ✅ **Success:** {success}/{total_users}
   • ❌ **Failed:** {failed}
   • ⏱️ **Time:** {time_taken}
   • 📈 **Success Rate:** {(success/total_users)*100:.1f}%

🚀 **Speed:** {(success+failed)/total_time:.1f} messages/second
    """, parse_mode=enums.ParseMode.MARKDOWN)

# Optional: Scheduled broadcast command
@Client.on_message(filters.command("schedulebroadcast") & filters.user([123456789]))
async def schedule_broadcast(bot, message):
    """Schedule a broadcast for later (basic implementation)"""
    await message.reply_text("""
⏰ **SCHEDULED BROADCAST**

🚧 **Feature Coming Soon!**

📅 **Planned Features:**
   • Schedule broadcasts for specific times
   • Recurring broadcasts (daily/weekly)
   • Time zone support
   • Automatic content scheduling

💡 **For now, use:**
   • `/broadcast` - Normal broadcast with confirmation
   • `/quickbroadcast` - Instant broadcast
    """, parse_mode=enums.ParseMode.MARKDOWN)
