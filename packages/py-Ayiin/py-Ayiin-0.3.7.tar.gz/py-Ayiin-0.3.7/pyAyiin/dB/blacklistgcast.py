
from ._core import mongodb

chatsdb = mongodb.chats

BLACKLIST_GCAST = []


async def get_blacklist_gcast() -> list:
    chats = chatsdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def blacklisted():
    chats = await get_blacklist_gcast()
    for chat in chats:
        chat_id = int(chat["chat_id"])
        if chat_id in BLACKLIST_GCAST:
            pass
        else:
            BLACKLIST_GCAST.append(int(chat["chat_id"]))
    return BLACKLIST_GCAST


async def is_blacklist_gcast(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_blacklist_gcast(chat_id: int):
    is_served = await is_blacklist_gcast(chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


async def remove_blacklist_gcast(chat_id: int):
    is_served = await is_blacklist_gcast(chat_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"chat_id": chat_id})
