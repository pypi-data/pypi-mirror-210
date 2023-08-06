from ._core import mongodb

ayiin_conf = mongodb.variable


async def set_var(var, value):
    p_variable = await ayiin_conf.find_one({"_id": var})
    if p_variable:
        await ayiin_conf.update_one({"_id": var}, {"$set": {"ayiin_conf": value}})
    else:
        await ayiin_conf.insert_one({"_id": var, "ayiin_conf": value})


async def get_var(var):
    custom_var = await ayiin_conf.find_one({"_id": var})
    if not custom_var:
        return None
    else:
        g_custom_var = custom_var["ayiin_conf"]
        return g_custom_var


async def del_var(var):
    custom_var = await ayiin_conf.find_one({"_id": var})
    if custom_var:
        await ayiin_conf.delete_one({"_id": var})
        return True
    else:
        return False
