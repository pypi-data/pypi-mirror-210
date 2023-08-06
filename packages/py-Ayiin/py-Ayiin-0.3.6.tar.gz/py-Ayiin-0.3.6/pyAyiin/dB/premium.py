
from ._core import mongodb

premsdb = mongodb.premium


async def get_prem() -> int:
    users = premsdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_prem(user_id: int) -> bool:
    user = await premsdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_prem(user_id: int):
    is_prems = await is_prem(user_id)
    if is_prems:
        return
    return await premsdb.insert_one({"user_id": user_id})


async def del_prem(user_id: int):
    is_prems = await is_prem(user_id)
    if not is_prems:
        return
    return await premsdb.delete_one({"user_id": user_id})


# CADANGAN
"""
async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True
"""
