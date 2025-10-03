# utils/db_manager.py
from dotenv import load_dotenv
load_dotenv()

import os
import motor.motor_asyncio

class DatabaseManager:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in environment variables.")
            
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client.wishes_bot_db
        self.birthdays = self.db.birthdays
        self.manual_wishes = self.db.manual_wishes
        self.birthday_role_log = self.db.birthday_role_log

    # --- Birthday Methods ---
    async def set_birthday(self, user_id: int, day: int, month: int, year: int):
        await self.birthdays.update_one(
            {"_id": user_id},
            {"$set": {"day": day, "month": month, "year": year}},
            upsert=True
        )

    async def get_birthday(self, user_id: int):
        return await self.birthdays.find_one({"_id": user_id})

    async def delete_birthday(self, user_id: int):
        result = await self.birthdays.delete_one({"_id": user_id})
        return result.deleted_count > 0

    # FIX: This function is synchronous, so we remove 'async'
    def get_birthdays_for_date(self, day: int, month: int):
        return self.birthdays.find({"day": day, "month": month})
    
    # --- Birthday Role Logging ---
    async def add_user_to_role_log(self, user_id: int, date_added: str):
        await self.birthday_role_log.update_one(
            {"_id": user_id},
            {"$set": {"date_added": date_added}},
            upsert=True
        )
        
    async def get_users_with_birthday_role(self):
        return self.birthday_role_log.find({})
    
    async def remove_user_from_role_log(self, user_id: int):
        await self.birthday_role_log.delete_one({"_id": user_id})

    # --- Manual Wish Methods (can be expanded) ---
    async def add_manual_wish(self, name: str, day: int, month: int, year: int, message: str, role_id: int):
        wish_doc = {
            "name": name,
            "day": day,
            "month": month,
            "year": year,
            "message": message,
            "role_id": role_id
        }
        await self.manual_wishes.insert_one(wish_doc)

db_manager = DatabaseManager()