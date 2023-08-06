
from ._core import mongodb

bluserdb = mongodb.blacklistuser


async def get_blacklistuser_count() -> int:
    users = bluserdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_user_blacklisted(user_id: int) -> bool:
    user = await bluserdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_user_blacklist(user_id: int):
    is_gbanned = await is_user_blacklisted(user_id)
    if is_gbanned:
        return
    return await bluserdb.insert_one({"user_id": user_id})


async def remove_user_blacklist(user_id: int):
    is_gbanned = await is_user_blacklisted(user_id)
    if not is_gbanned:
        return
    return await bluserdb.delete_one({"user_id": user_id})
