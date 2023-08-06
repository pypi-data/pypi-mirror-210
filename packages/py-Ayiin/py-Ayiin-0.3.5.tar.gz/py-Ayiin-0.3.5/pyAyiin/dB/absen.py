from typing import Dict, List

from ._core import mongodb

absendb = mongodb.absen


async def get_notes_count() -> dict:
    chats_count = 0
    absen_count = 0
    async for chat in absendb.find({"chat_id": {"$exists": 1}}):
        absen_name = await get_absen(chat["chat_id"])
        absen_count += len(absen_name)
        chats_count += 1
    return {"chats_count": chats_count, "absen_count": absen_count}


async def _get_absen(chat_id: int) -> Dict[str, int]:
    _absen = await absendb.find_one({"chat_id": chat_id})
    if not _absen:
        return {}
    return _absen["absen"]


async def get_absen(chat_id: int) -> List[str]:
    _absen = []
    for abse in await _get_absen(chat_id):
        _absen.append(abse)
    return _absen


async def save_absen(chat_id: int, name: str, asbes: dict):
    name = name.lower().strip()
    _absen = await _get_absen(chat_id)
    _absen[name] = asbes

    await absendb.update_one(
        {"chat_id": chat_id}, {"$set": {"absen": _absen}}, upsert=True
    )


async def del_absen(chat_id: int) -> bool:
    absensd = await _get_absen(chat_id)
    for name in absensd:
        del absensd[name]
        await absendb.update_one(
            {"chat_id": chat_id},
            {"$set": {"absen": absensd}},
            upsert=True,
        )
        return True
    return False
