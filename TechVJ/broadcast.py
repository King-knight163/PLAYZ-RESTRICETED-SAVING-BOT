from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import db
from pyrogram import Client, filters, enums
import asyncio
import datetime
import time
import json
import random
from threading import Thread
import schedule

# Global storage for broadcast data
broadcast_stats = {}
scheduled_broadcasts = {}
auto_broadcasts = {}
batch_broadcasts = {}
broadcast_scheduler_running = False

class BroadcastScheduler:
    def __init__(self):
        self.running = False
        
    async def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            return
            
        self.running = True
        while self.running:
            try:
                await self.check_scheduled_broadcasts()
                await self.check_auto_broadcasts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def check_scheduled_broadcasts(self):
        """Check and execute scheduled broadcasts"""
        current_time = int(time.time())
        
        for broadcast_id, broadcast_data in list(scheduled_broadcasts.items()):
            if broadcast_data['execute_time'] <= current_time:
                await self.execute_scheduled_broadcast(broadcast_id, broadcast_data)
                del scheduled_broadcasts[broadcast_id]
    
    async def check_auto_broadcasts(self):
        """Check and execute auto-repeat broadcasts"""
        current_time = int(time.time())
        
        for auto_id, auto_data in list(auto_broadcasts.items()):
            if auto_data['next_run'] <= current_time:
                # Execute broadcast
                success = await self.execute_auto_broadcast(auto_id, auto_data)
                
                if success:
                    # Update repeat count
                    auto_data['executed_count'] += 1
                    
                    # Check if more repeats needed
                    if auto_data['executed_count'] >= auto_data['total_repeats']:
                        # Delete from auto broadcasts
                        del auto_broadcasts[auto_id]
                        print(f"Auto broadcast {auto_id} completed all {auto_data['total_repeats']} repeats")
                    else:
                        # Schedule next run
                        auto_data['next_run'] = current_time + auto_data['interval_seconds']
                        print(f"Auto broadcast {auto_id} scheduled for next run: {auto_data['next_run']}")

    async def execute_scheduled_broadcast(self, broadcast_id, broadcast_data):
        """Execute a scheduled broadcast"""
        try:
            print(f"Executing scheduled broadcast: {broadcast_id}")
            # Implementation for scheduled broadcast execution
        except Exception as e:
            print(f"Error executing scheduled broadcast {broadcast_id}: {e}")

    async def execute_auto_broadcast(self, auto_id, auto_data):
        """Execute an auto-repeat broadcast"""
        try:
            print(f"Executing auto broadcast: {auto_id}")
            
            # Handle batch broadcasts (rotate messages)
            if auto_data['type'] == 'batch':
                current_index = auto_data['current_message_index']
                message_data = auto_data['messages'][current_index]
                
                # Send the current message
                success = await self.send_auto_message(message_data, auto_data, auto_id)
                
                # Move to next message in batch
                auto_data['current_message_index'] = (current_index + 1) % len(auto_data['messages'])
                
                return success
            else:
                # Single message auto broadcast
                return await self.send_auto_message(auto_data['message_data'], auto_data, auto_id)
                
        except Exception as e:
            print(f"Error executing auto broadcast {auto_id}: {e}")
            return False

    async def send_auto_message(self, message_data, auto_data, auto_id):
        """Send auto broadcast message to all users with pinning"""
        try:
            users = await db.get_all_users()
            success_count = 0
            
            async for user in users:
                if 'id' in user:
                    user_id = int(user['id'])
                    
                    try:
                        # Send message
                        if message_data['type'] == 'text':
                            sent_msg = await bot.send_message(
                                user_id, 
                                message_data['content'],
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                        elif message_data['type'] == 'photo':
                            sent_msg = await bot.send_photo(
                                user_id,
                                message_data['file_id'],
                                caption=message_data['caption'],
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                        # Add more message types as needed
                        
                        # Pin the message if enabled
                        if auto_data.get('auto_pin', True):
                            try:
                                await bot.pin_chat_message(user_id, sent_msg.id, disable_notification=True)
                            except:
                                pass  # Ignore pin errors
                        
                        success_count += 1
                        
                    except Exception as e:
                        continue
                        
            print(f"Auto broadcast {auto_id} sent to {success_count} users")
            return True
            
        except Exception as e:
            print(f"Error sending auto message: {e}")
            return False

# Initialize scheduler
scheduler = BroadcastScheduler()

async def broadcast_messages(user_id, message, auto_pin=False):
    """Enhanced broadcast function with auto-pin feature"""
    try:
        sent_msg = await message.copy(chat_id=user_id, protect_content=False)
        
        # Auto-pin if enabled
        if auto_pin:
            try:
                await sent_msg.pin(disable_notification=True)
            except:
                pass  # Ignore pin errors
        
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message, auto_pin)
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

# Regular Broadcast (existing code...)
@Client.on_message(filters.command("broadcast") & filters.user([7107162691]) & filters.reply)
async def advanced_broadcast(bot, message):
    """Enhanced broadcast command with auto-pin option"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "❌ **Reply Required**

Reply to a message that you want to broadcast to all users.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    user_stats = await get_user_statistics()
    total_users = user_stats["total"]
    
    if total_users == 0:
        return await message.reply_text("❌ **No users found in database!**", parse_mode=enums.ParseMode.MARKDOWN)
    
    confirm_text = f"""
📡 **BROADCAST CONFIRMATION**

📊 **Target Audience:** {total_users} users
📝 **Message Preview:** {b_msg.text[:100] if b_msg.text else "Media message"}{"..." if b_msg.text and len(b_msg.text) > 100 else ""}

⚙️ **Broadcast Options:**
"""
    
    buttons = [
        [
            InlineKeyboardButton("📌 Broadcast + Auto Pin", callback_data=f"broadcast_pin_{message.id}"),
            InlineKeyboardButton("📤 Normal Broadcast", callback_data=f"broadcast_normal_{message.id}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
    ]
    
    await message.reply_text(
        confirm_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Scheduled Broadcast
@Client.on_message(filters.command("schedulebroadcast") & filters.user([7107162691]) & filters.reply)
async def schedule_broadcast(bot, message):
    """Schedule a broadcast for specific date and time"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "❌ **Reply Required**

Reply to a message that you want to schedule for broadcast.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    schedule_text = """
⏰ **SCHEDULE BROADCAST**

📅 **When do you want to send this broadcast?**

⏰ **Quick Options:**
"""
    
    current_time = int(time.time())
    buttons = [
        [
            InlineKeyboardButton("🕐 1 Hour Later", callback_data=f"schedule_{current_time + 3600}_{message.id}"),
            InlineKeyboardButton("🕕 6 Hours Later", callback_data=f"schedule_{current_time + 21600}_{message.id}")
        ],
        [
            InlineKeyboardButton("📅 Tomorrow 9 AM", callback_data=f"schedule_{current_time + 86400}_{message.id}"),
            InlineKeyboardButton("🌙 Tonight 10 PM", callback_data=f"schedule_{current_time + 43200}_{message.id}")
        ],
        [
            InlineKeyboardButton("⏰ Custom Time", callback_data=f"schedule_custom_{message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_schedule")
        ]
    ]
    
    await message.reply_text(
        schedule_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Auto-Repeat Broadcast
@Client.on_message(filters.command("autobroadcast") & filters.user([7107162691]) & filters.reply)
async def auto_repeat_broadcast(bot, message):
    """Create auto-repeating broadcasts"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "❌ **Reply Required**

Reply to a message for auto-repeat broadcasting.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    auto_text = """
🔄 **AUTO-REPEAT BROADCAST**

⏱️ **Select Repeat Interval:**

🕐 **Time Intervals:**
"""
    
    buttons = [
        [
            InlineKeyboardButton("🕐 Every 1 Minute", callback_data=f"auto_60_{message.id}"),
            InlineKeyboardButton("🕕 Every 5 Minutes", callback_data=f"auto_300_{message.id}")
        ],
        [
            InlineKeyboardButton("🕘 Every 30 Minutes", callback_data=f"auto_1800_{message.id}"),
            InlineKeyboardButton("🕐 Every 1 Hour", callback_data=f"auto_3600_{message.id}")
        ],
        [
            InlineKeyboardButton("📅 Every 12 Hours", callback_data=f"auto_43200_{message.id}"),
            InlineKeyboardButton("🌅 Every 24 Hours", callback_data=f"auto_86400_{message.id}")
        ],
        [
            InlineKeyboardButton("📆 Every Week", callback_data=f"auto_604800_{message.id}"),
            InlineKeyboardButton("🗓️ Every Month", callback_data=f"auto_2592000_{message.id}")
        ],
        [
            InlineKeyboardButton("📊 Custom Interval", callback_data=f"auto_custom_{message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_auto")
        ]
    ]
    
    await message.reply_text(
        auto_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Batch Auto-Broadcast
@Client.on_message(filters.command("batchbroadcast") & filters.user([7107162691]))
async def batch_auto_broadcast(bot, message):
    """Create batch auto-broadcasts with rotating messages"""
    batch_text = """
📦 **BATCH AUTO-BROADCAST**

🔄 **How it works:**
   • Add multiple messages to a batch
   • Set repeat interval
   • Bot will rotate through messages
   • Each repeat sends next message in sequence

📝 **Commands:**
   • `/addbatch` - Add message to current batch
   • `/viewbatch` - View current batch messages
   • `/startbatch` - Start batch auto-broadcast
   • `/clearbatch` - Clear current batch

💡 **Example:**
   Batch: ["Hello", "How are you?", "Have a great day!"]
   Interval: 1 hour
   
   Hour 1: "Hello" → All users
   Hour 2: "How are you?" → All users  
   Hour 3: "Have a great day!" → All users
   Hour 4: "Hello" → All users (cycle repeats)
"""
    
    buttons = [
        [
            InlineKeyboardButton("➕ Add Message to Batch", callback_data="add_to_batch"),
            InlineKeyboardButton("👀 View Current Batch", callback_data="view_batch")
        ],
        [
            InlineKeyboardButton("🚀 Start Batch Broadcast", callback_data="start_batch"),
            InlineKeyboardButton("🗑️ Clear Batch", callback_data="clear_batch")
        ]
    ]
    
    await message.reply_text(
        batch_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Callback handlers for auto-broadcast interval selection
@Client.on_callback_query(filters.regex("auto_"))
async def handle_auto_interval(bot, callback_query):
    """Handle auto-broadcast interval selection"""
    data_parts = callback_query.data.split("_")
    
    if len(data_parts) < 3:
        await callback_query.answer("❌ Invalid data!", show_alert=True)
        return
    
    interval_seconds = int(data_parts[1])
    msg_id = int(data_parts[2])
    
    # Now ask for repeat count
    repeat_text = f"""
🔄 **AUTO-BROADCAST SETUP**

⏱️ **Interval:** Every {format_time_interval(interval_seconds)}
📌 **Auto-Pin:** Messages will be automatically pinned

🔢 **How many times should this repeat?**

💡 **Repeat Options:**
"""
    
    buttons = [
        [
            InlineKeyboardButton("🔢 5 Times", callback_data=f"repeat_5_{interval_seconds}_{msg_id}"),
            InlineKeyboardButton("🔢 10 Times", callback_data=f"repeat_10_{interval_seconds}_{msg_id}")
        ],
        [
            InlineKeyboardButton("🔢 25 Times", callback_data=f"repeat_25_{interval_seconds}_{msg_id}"),
            InlineKeyboardButton("🔢 50 Times", callback_data=f"repeat_50_{interval_seconds}_{msg_id}")
        ],
        [
            InlineKeyboardButton("🔢 100 Times", callback_data=f"repeat_100_{interval_seconds}_{msg_id}"),
            InlineKeyboardButton("♾️ Unlimited", callback_data=f"repeat_999999_{interval_seconds}_{msg_id}")
        ],
        [
            InlineKeyboardButton("📝 Custom Count", callback_data=f"repeat_custom_{interval_seconds}_{msg_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_auto")
        ]
    ]
    
    await callback_query.edit_message_text(
        repeat_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("repeat_"))
async def handle_repeat_count(bot, callback_query):
    """Handle repeat count selection and create auto-broadcast"""
    data_parts = callback_query.data.split("_")
    
    if len(data_parts) < 4:
        await callback_query.answer("❌ Invalid data!", show_alert=True)
        return
    
    repeat_count = int(data_parts[1])
    interval_seconds = int(data_parts[2])
    msg_id = int(data_parts[3])
    
    try:
        # Get the original message
        original_msg = await bot.get_messages(callback_query.message.chat.id, msg_id)
        b_msg = original_msg.reply_to_message
        
        if not b_msg:
            await callback_query.answer("❌ Original message not found!", show_alert=True)
            return
        
        # Create auto-broadcast entry
        auto_id = f"auto_{int(time.time())}_{random.randint(1000, 9999)}"
        current_time = int(time.time())
        
        auto_broadcasts[auto_id] = {
            'type': 'single',
            'message_data': {
                'type': 'text' if b_msg.text else 'media',
                'content': b_msg.text,
                'file_id': b_msg.photo.file_id if b_msg.photo else None,
                'caption': b_msg.caption if b_msg.caption else None
            },
            'interval_seconds': interval_seconds,
            'total_repeats': repeat_count,
            'executed_count': 0,
            'next_run': current_time + interval_seconds,
            'auto_pin': True,
            'created_by': callback_query.from_user.id,
            'created_at': current_time
        }
        
        # Start scheduler if not running
        global broadcast_scheduler_running
        if not broadcast_scheduler_running:
            broadcast_scheduler_running = True
            asyncio.create_task(scheduler.start_scheduler())
        
        success_text = f"""
✅ **AUTO-BROADCAST CREATED!**

🆔 **Broadcast ID:** `{auto_id}`
⏱️ **Interval:** Every {format_time_interval(interval_seconds)}
🔢 **Total Repeats:** {repeat_count if repeat_count < 999999 else 'Unlimited'}
📌 **Auto-Pin:** Enabled
⏰ **First Run:** {datetime.datetime.fromtimestamp(auto_broadcasts[auto_id]['next_run']).strftime('%Y-%m-%d %H:%M:%S')}

🎯 **Status:** Active and scheduled
📊 **Progress:** 0/{repeat_count if repeat_count < 999999 else '∞'} completed

💡 **Management Commands:**
   • `/listauto` - View all active auto-broadcasts
   • `/stopauto {auto_id}` - Stop specific auto-broadcast
   • `/pauseauto {auto_id}` - Pause auto-broadcast
"""
        
        buttons = [
            [
                InlineKeyboardButton("📊 View All Auto-Broadcasts", callback_data="list_auto_broadcasts"),
                InlineKeyboardButton("⏹️ Stop This Auto-Broadcast", callback_data=f"stop_auto_{auto_id}")
            ]
        ]
        
        await callback_query.edit_message_text(
            success_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await callback_query.answer(f"❌ Error creating auto-broadcast: {str(e)[:100]}", show_alert=True)

def format_time_interval(seconds):
    """Format seconds into human readable time"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds // 60} minutes"
    elif seconds < 86400:
        return f"{seconds // 3600} hours"
    elif seconds < 604800:
        return f"{seconds // 86400} days"
    elif seconds < 2592000:
        return f"{seconds // 604800} weeks"
    else:
        return f"{seconds // 2592000} months"

# Auto-broadcast management commands
@Client.on_message(filters.command("listauto") & filters.user([7107162691]))
async def list_auto_broadcasts(bot, message):
    """List all active auto-broadcasts"""
    if not auto_broadcasts:
        return await message.reply_text(
            "📭 **No Active Auto-Broadcasts**

Use `/autobroadcast` to create one.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    list_text = "🔄 **ACTIVE AUTO-BROADCASTS**

"
    
    for auto_id, auto_data in auto_broadcasts.items():
        progress = f"{auto_data['executed_count']}/{auto_data['total_repeats']}" if auto_data['total_repeats'] < 999999 else f"{auto_data['executed_count']}/∞"
        next_run = datetime.datetime.fromtimestamp(auto_data['next_run']).strftime('%H:%M:%S')
        broadcast_type = "📦 Batch" if auto_data['type'] == 'batch' else "📝 Single"
        
        list_text += f"""
{broadcast_type} **ID:** `{auto_id}`
⏱️ **Interval:** {format_time_interval(auto_data['interval_seconds'])}
📊 **Progress:** {progress}
⏰ **Next Run:** {next_run}
📌 **Auto-Pin:** {'✅' if auto_data.get('auto_pin') else '❌'}
"""
        
        # Add batch-specific info
        if auto_data['type'] == 'batch':
            current_msg = auto_data.get('current_message_index', 0) + 1
            total_msgs = len(auto_data.get('messages', []))
            list_text += f"🔄 **Current Message:** {current_msg}/{total_msgs}
"
        
        list_text += "
"
    
    buttons = [
        [
            InlineKeyboardButton("⏹️ Stop All", callback_data="stop_all_auto"),
            InlineKeyboardButton("📊 Detailed Stats", callback_data="auto_detailed_stats")
        ]
    ]
    
    await message.reply_text(
        list_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("auto_detailed_stats"))
async def show_detailed_auto_stats(bot, callback_query):
    """Show detailed statistics of all auto-broadcasts"""
    if not auto_broadcasts:
        await callback_query.answer("❌ No active auto-broadcasts!", show_alert=True)
        return
    
    total_sent = sum(auto_data['executed_count'] for auto_data in auto_broadcasts.values())
    single_count = sum(1 for auto_data in auto_broadcasts.values() if auto_data['type'] == 'single')
    batch_count = sum(1 for auto_data in auto_broadcasts.values() if auto_data['type'] == 'batch')
    
    stats_text = f"""
📊 **AUTO-BROADCAST ANALYTICS**

🔢 **Overview:**
   • **Total Active:** {len(auto_broadcasts)}
   • **Single Broadcasts:** {single_count}
   • **Batch Broadcasts:** {batch_count}
   • **Total Messages Sent:** {total_sent}

📈 **Performance:**
"""
    
    for auto_id, auto_data in list(auto_broadcasts.items())[:5]:  # Show top 5
        completion = (auto_data['executed_count'] / auto_data['total_repeats']) * 100 if auto_data['total_repeats'] < 999999 else 0
        stats_text += f"""
   • `{auto_id[:8]}...`: {completion:.1f}% complete
"""
    
    if len(auto_broadcasts) > 5:
        stats_text += f"
   ... and {len(auto_broadcasts) - 5} more"
    
    await callback_query.edit_message_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_auto_list")]]),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("back_to_auto_list"))
async def back_to_auto_list(bot, callback_query):
    """Go back to auto-broadcast list"""
    # Redirect to list command
    await list_auto_broadcasts(bot, callback_query.message)

@Client.on_message(filters.command("stopauto") & filters.user([7107162691]))
async def stop_auto_broadcast(bot, message):
    """Stop a specific auto-broadcast"""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/stopauto <auto_id>`

Use `/listauto` to see active broadcasts.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    auto_id = message.command[1]
    
    if auto_id not in auto_broadcasts:
        return await message.reply_text(
            f"❌ **Auto-broadcast `{auto_id}` not found!**

Use `/listauto` to see active broadcasts.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    # Remove from active broadcasts
    auto_data = auto_broadcasts[auto_id]
    del auto_broadcasts[auto_id]
    
    broadcast_type = "Batch" if auto_data['type'] == 'batch' else "Single"
    
    await message.reply_text(
        f"⏹️ **{broadcast_type} Auto-Broadcast Stopped!**

🆔 **ID:** `{auto_id}`
📊 **Completed:** {auto_data['executed_count']}/{auto_data['total_repeats']} repeats
⏱️ **Runtime:** {format_time_interval(int(time.time()) - auto_data['created_at'])}

✅ Successfully removed from schedule.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Pause and resume auto-broadcasts
@Client.on_message(filters.command("pauseauto") & filters.user([7107162691]))
async def pause_auto_broadcast(bot, message):
    """Pause a specific auto-broadcast"""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/pauseauto <auto_id>`

Use `/listauto` to see active broadcasts.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    auto_id = message.command[1]
    
    if auto_id not in auto_broadcasts:
        return await message.reply_text(
            f"❌ **Auto-broadcast `{auto_id}` not found!**",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    # Set next run to far future (paused state)
    auto_broadcasts[auto_id]['paused'] = True
    auto_broadcasts[auto_id]['paused_at'] = int(time.time())
    auto_broadcasts[auto_id]['next_run'] = int(time.time()) + 999999999  # Far future
    
    await message.reply_text(
        f"⏸️ **Auto-Broadcast Paused!**

🆔 **ID:** `{auto_id}`
📊 **Progress:** {auto_broadcasts[auto_id]['executed_count']}/{auto_broadcasts[auto_id]['total_repeats']}

💡 Use `/resumeauto {auto_id}` to resume.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("resumeauto") & filters.user([7107162691]))
async def resume_auto_broadcast(bot, message):
    """Resume a paused auto-broadcast"""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/resumeauto <auto_id>`

Use `/listauto` to see active broadcasts.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    auto_id = message.command[1]
    
    if auto_id not in auto_broadcasts:
        return await message.reply_text(
            f"❌ **Auto-broadcast `{auto_id}` not found!**",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    if not auto_broadcasts[auto_id].get('paused', False):
        return await message.reply_text(
            f"❌ **Auto-broadcast `{auto_id}` is not paused!**",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    # Resume broadcast
    current_time = int(time.time())
    auto_broadcasts[auto_id]['paused'] = False
    auto_broadcasts[auto_id]['next_run'] = current_time + auto_broadcasts[auto_id]['interval_seconds']
    
    if 'paused_at' in auto_broadcasts[auto_id]:
        del auto_broadcasts[auto_id]['paused_at']
    
    await message.reply_text(
        f"▶️ **Auto-Broadcast Resumed!**

🆔 **ID:** `{auto_id}`
⏰ **Next Run:** {datetime.datetime.fromtimestamp(auto_broadcasts[auto_id]['next_run']).strftime('%H:%M:%S')}

✅ Broadcasting will continue as scheduled.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# Batch broadcast management
@Client.on_message(filters.command("addbatch") & filters.user([7107162691]) & filters.reply)
async def add_to_batch(bot, message):
    """Add message to current batch"""
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "❌ **Reply Required**

Reply to a message to add it to batch.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    # Initialize batch if doesn't exist
    user_id = message.from_user.id
    if user_id not in batch_broadcasts:
        batch_broadcasts[user_id] = {
            'messages': [],
            'created_at': int(time.time())
        }
    
    # Add message to batch
    message_data = {
        'type': 'text' if b_msg.text else 'media',
        'content': b_msg.text[:100] if b_msg.text else 'Media message',
        'full_content': b_msg.text,
        'file_id': b_msg.photo.file_id if b_msg.photo else None,
        'caption': b_msg.caption if b_msg.caption else None,
        'message_id': b_msg.id
    }
    
    batch_broadcasts[user_id]['messages'].append(message_data)
    
    batch_count = len(batch_broadcasts[user_id]['messages'])
    
    buttons = [
        [
            InlineKeyboardButton("➕ Add More", callback_data="add_more_batch"),
            InlineKeyboardButton("👀 View Batch", callback_data="view_current_batch")
        ],
        [
            InlineKeyboardButton("🚀 Start Batch", callback_data="start_batch_broadcast"),
            InlineKeyboardButton("🗑️ Clear Batch", callback_data="clear_batch")
        ]
    ]
    
    await message.reply_text(
        f"✅ **Message Added to Batch!**

📦 **Batch Size:** {batch_count} messages
📝 **Latest:** {message_data['content']}

🎯 **Next Steps:**",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("viewbatch") & filters.user([7107162691]))
async def view_batch(bot, message):
    """View current batch messages"""
    user_id = message.from_user.id
    
    if user_id not in batch_broadcasts or not batch_broadcasts[user_id]['messages']:
        return await message.reply_text(
            "📭 **No Batch Found**

Use `/addbatch` (reply to message) to add messages to batch.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    batch_data = batch_broadcasts[user_id]
    batch_text = f"📦 **CURRENT BATCH ({len(batch_data['messages'])} messages)**

"
    
    for i, msg in enumerate(batch_data['messages'], 1):
        batch_text += f"**{i}.** {msg['content']}
"
        if i >= 10:  # Limit display to 10 messages
            batch_text += f"... and {len(batch_data['messages']) - 10} more messages
"
            break
    
    created_ago = format_time_interval(int(time.time()) - batch_data['created_at'])
    batch_text += f"
🕐 **Created:** {created_ago} ago"
    
    buttons = [
        [
            InlineKeyboardButton("🚀 Start Batch Broadcast", callback_data="start_batch_broadcast"),
            InlineKeyboardButton("🗑️ Clear Batch", callback_data="clear_batch")
        ]
    ]
    
    await message.reply_text(
        batch_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex("view_current_batch"))
async def view_current_batch_callback(bot, callback_query):
    """View current batch via callback"""
    await view_batch(bot, callback_query.message)
