
from ._core import mongodb

sudoersdb = mongodb.sudoers


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


async def check_sudo(sudo_id):
    already_sudo = await sudoersdb.find_one({"sudo": "sudo"})
    if already_sudo:
        sudo_list = [int(sudo_id) for sudo_id in already_sudo.get("sudo_id")]
        if int(sudo_id) in sudo_list:
            return True
        else:
            return False
    else:
        return False
