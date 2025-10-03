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

    async def get_all_manual_wishes(self):
        """Get all manual wishes"""
        return await self.manual_wishes.find({}).to_list(length=None)

    async def delete_manual_wish(self, wish_id: str):
        """Delete a manual wish by ID"""
        from bson import ObjectId
        result = await self.manual_wishes.delete_one({"_id": ObjectId(wish_id)})
        return result.deleted_count > 0

    # --- Analytics Methods ---
    async def get_total_birthdays(self):
        """Get total count of registered birthdays"""
        return await self.birthdays.count_documents({})

    async def get_all_birthdays(self):
        """Get all birthdays"""
        return await self.birthdays.find({}).to_list(length=None)

    async def get_birthdays_by_month(self):
        """Get birthday count by month"""
        pipeline = [
            {"$group": {"_id": "$month", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        result = await self.birthdays.aggregate(pipeline).to_list(length=None)
        return result

    async def get_upcoming_birthdays(self, days: int = 30):
        """Get upcoming birthdays within specified days"""
        from datetime import datetime, timedelta
        today = datetime.now()
        birthdays = await self.get_all_birthdays()
        
        upcoming = []
        for bday in birthdays:
            # Create a date for this year
            try:
                this_year_birthday = datetime(today.year, bday['month'], bday['day'])
                if this_year_birthday < today:
                    # Try next year if already passed
                    this_year_birthday = datetime(today.year + 1, bday['month'], bday['day'])
                
                days_until = (this_year_birthday - today).days
                if 0 <= days_until <= days:
                    upcoming.append({
                        **bday,
                        'days_until': days_until
                    })
            except ValueError:
                # Invalid date (e.g., Feb 29 on non-leap year)
                continue
        
        return sorted(upcoming, key=lambda x: x['days_until'])

    async def get_total_manual_wishes(self):
        """Get total count of manual wishes"""
        return await self.manual_wishes.count_documents({})

db_manager = DatabaseManager()