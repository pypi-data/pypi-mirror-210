from motor.motor_asyncio import AsyncIOMotorClient as Bot

from pyAyiin.config import Var


# Mongo DB
_mongo_async_ = Bot(Var.MONGO_URI)
mongodb = _mongo_async_.AyiinXd
