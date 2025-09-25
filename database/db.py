import motor.motor_asyncio
import time
import random
import string
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            role = "free",
            expiry = 0,
            code = None,
            usage = {"batches": 0, "files": 0, "last_reset": int(time.time())}
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session') if user else None

    # NEW FUNCTIONS FOR ROLE MANAGEMENT
    async def get_user(self, id):
        return await self.col.find_one({'id': int(id)})

    async def update_user_role(self, id, role, expiry=0):
        await self.col.update_one({'id': int(id)}, {'$set': {'role': role, 'expiry': expiry}})

    async def set_user_code(self, id, code):
        await self.col.update_one({'id': int(id)}, {'$set': {'code': code}})

    async def get_user_code(self, id):
        user = await self.col.find_one({'id': int(id)}, {'code': 1})
        return user.get('code') if user else None

    async def get_user_role(self, id):
        user = await self.col.find_one({'id': int(id)}, {'role': 1, 'expiry': 1})
        if not user:
            return "free"
        role = user.get("role", "free")
        expiry = user.get("expiry", 0)
        # Check expiry for freemium users
        if role == "freemium" and expiry < int(time.time()):
            await self.update_user_role(id, "free", 0)
            return "free"
        return role

    async def get_user_usage(self, id):
        user = await self.col.find_one({'id': int(id)}, {'usage': 1})
        if not user:
            return {"batches": 0, "files": 0, "last_reset": int(time.time())}
        return user.get('usage', {"batches": 0, "files": 0, "last_reset": int(time.time())})

    async def update_user_usage(self, id, batches_increment=0, files_increment=0):
        usage = await self.get_user_usage(id)
        current_time = int(time.time())
        
        # Reset usage daily (24 hours)
        if usage.get("last_reset", 0) + 86400 < current_time:
            usage = {"batches": 0, "files": 0, "last_reset": current_time}
        
        usage["batches"] += batches_increment
        usage["files"] += files_increment
        usage["last_reset"] = usage.get("last_reset", current_time)
        
        await self.col.update_one({'id': int(id)}, {'$set': {'usage': usage}})

    async def reset_user_usage(self, id):
        current_time = int(time.time())
        usage = {"batches": 0, "files": 0, "last_reset": current_time}
        await self.col.update_one({'id': int(id)}, {'$set': {'usage': usage}})

    async def generate_or_get_code(self, id):
        code = await self.get_user_code(id)
        if code:
            return code
        # Generate new random code
        new_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        await self.set_user_code(id, new_code)
        return new_code

    async def add_freemium_user(self, id, code, duration=86400):  # 24 hours default
        expiry = int(time.time()) + duration
        await self.update_user_role(id, "freemium", expiry)
        await self.reset_user_usage(id)  # Reset usage when freemium is added

    async def can_forward(self, id):
        role = await self.get_user_role(id)
        usage = await self.get_user_usage(id)
        
        # Define limits for each role
        limits = {
            "freemium": {"files_per_batch": 3, "daily_batches": 4},
            "standard": {"files_per_batch": 20, "daily_batches": 10},
            "pro": {"files_per_batch": 50, "daily_batches": 15},
            "elite": {"files_per_batch": 100, "daily_batches": 15},
            "premium": {"files_per_batch": 1000, "daily_batches": 1000},
            "free": {"files_per_batch": 0, "daily_batches": 0}
        }
        
        limit = limits.get(role, limits["free"])
        
        # Check if user is free (not verified)
        if role == "free":
            return False, "Please verify first using /verify to get access."
        
        # Check daily batch limit
        if usage["batches"] >= limit["daily_batches"]:
            return False, f"Daily batch limit reached. You can use {limit['daily_batches']} batches per day."
        
        return True, ""

    async def get_user_stats(self, id):
        user = await self.get_user(id)
        if not user:
            return None
        
        role = await self.get_user_role(id)
        usage = await self.get_user_usage(id)
        expiry = user.get("expiry", 0)
        
        return {
            "role": role,
            "usage": usage,
            "expiry": expiry,
            "expiry_readable": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry)) if expiry else "No expiry"
        }

db = Database(DB_URI, DB_NAME)
