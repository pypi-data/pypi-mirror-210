from ._core import mongodb

collection = mongodb.logdb

# pmlogs


async def is_pm_logs(on_off: int) -> bool:
    onoff = await collection.find_one({"on_off": on_off})
    if not onoff:
        return False
    return True


async def add_pm_on(on_off: int):
    is_on = await is_pm_logs(on_off)
    if is_on:
        return
    return await collection.insert_one({"on_off": on_off})


async def add_pm_off(on_off: int):
    is_off = await is_pm_logs(on_off)
    if not is_off:
        return
    return await collection.delete_one({"on_off": on_off})


async def is_grup_logs(on_off: int) -> bool:
    onoff = await collection.find_one({"on_off": on_off})
    if not onoff:
        return False
    return True


async def add_grup_on(on_off: int):
    is_on = await is_grup_logs(on_off)
    if is_on:
        return
    return await collection.insert_one({"on_off": on_off})


async def add_grup_off(on_off: int):
    is_off = await is_grup_logs(on_off)
    if not is_off:
        return
    return await collection.delete_one({"on_off": on_off})
