
from ._core import mongodb

gbansdb = mongodb.gban


async def gbanned_users() -> int:
    users = gbansdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_gbanned(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_gbanned(user_id: int):
    is_gban = await is_gbanned(user_id)
    if is_gban:
        return
    return await gbansdb.insert_one({"user_id": user_id})


async def remove_gbanned(user_id: int):
    is_gban = await is_gbanned(user_id)
    if not is_gban:
        return
    return await gbansdb.delete_one({"user_id": user_id})
