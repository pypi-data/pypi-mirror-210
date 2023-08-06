# Ayiin - Userbot
# Copyright (C) 2022-2023 @AyiinXd
#
# This file is a part of < https://github.com/AyiinXd/Ayiin-Userbot >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/AyiinXd/Ayiin-Userbot/blob/main/LICENSE/>.
#
# FROM Ayiin-Userbot <https://github.com/AyiinXd/Ayiin-Userbot>
# t.me/AyiinChat & t.me/AyiinSupport


# ========================×========================
#            Jangan Hapus Credit Ngentod
# ========================×========================

import logging
import sys

from pyAyiin.config import Var as Variable

from ..methods.helpers import Helpers
from ..methods.hosting import where_hosted

from .client import *


logs = logging.getLogger(__name__)
HOSTED_ON = where_hosted()
Var = Variable()
Xd = Helpers()


async def ayiin_client(client):
    try:
        await client.join_chat("AyiinChat")
        await client.join_chat("AyiinSupport")
        await client.join_chat("StoryAyiin")
    except Exception:
        pass


clients = []
client_id = []


async def StartPyrogram():
    try:
        bot_plugins = Xd.import_module(
            "assistant/",
            display_module=False,
            exclude=Var.NO_LOAD,
        )
        logs.info(f"{bot_plugins} Total Plugins Bot")
        plugins = Xd.import_module(
            "AyiinXd/",
            display_module=False,
            exclude=Var.NO_LOAD,
        )
        logs.info(f"{plugins} Total Plugins User")
    except BaseException as e:
        logs.info(e)
        sys.exit()
    if Var.TELEBOT == "True":
        logs.info('Starting Telethon Bot...')
        await TeleBot.start(bot_token=Var.BOT_TOKEN)
        me = await TeleBot.get_me()
        bot_id = me.id
        if me.last_name:
            bot_name = me.first_name + " " + me.last_name
        else:
            bot_name = me.first_name
        logs.info(
            f"TeleBot in {bot_name} | [ {bot_id} ]"
        )
        client_id.append(bot_id)
    if tgbot:
        await tgbot.start()
        me = await tgbot.get_me()
        tgbot.id = me.id
        tgbot.mention = me.mention
        tgbot.username = me.username
        if me.last_name:
            tgbot.name = me.first_name + " " + me.last_name
        else:
            tgbot.name = me.first_name
        logs.info(
            f"TgBot in {tgbot.name} | [ {tgbot.id} ]"
        )
        client_id.append(tgbot.id)
    if AYIIN1:
        try:
            await AYIIN1.start()
            clients.append(1)
            await ayiin_client(AYIIN1)
            me = await AYIIN1.get_me()
            AYIIN1.id = me.id
            AYIIN1.mention = me.mention
            AYIIN1.username = me.username
            if me.last_name:
                AYIIN1.name = me.first_name + " " + me.last_name
            else:
                AYIIN1.name = me.first_name
            #AYIIN1.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN1 in {AYIIN1.name} | [ {AYIIN1.id} ]"
            )
            client_id.append(AYIIN1.id)
        except Exception as e:
            logs.info(f"[STRING_1] ERROR: {e}")
    if AYIIN2:
        try:
            await AYIIN2.start()
            clients.append(2)
            await ayiin_client(AYIIN2)
            me = await AYIIN2.get_me()
            AYIIN2.id = me.id
            AYIIN2.mention = me.mention
            AYIIN2.username = me.username
            if me.last_name:
                AYIIN2.name = me.first_name + " " + me.last_name
            else:
                AYIIN2.name = me.first_name
            #AYIIN2.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN2 in {AYIIN2.name} | [ {AYIIN2.id} ]"
            )
            client_id.append(AYIIN2.id)
        except Exception as e:
            logs.info(f"[STRING_2] ERROR: {e}")
    if AYIIN3:
        try:
            await AYIIN3.start()
            clients.append(3)
            await ayiin_client(AYIIN3)
            me = await AYIIN3.get_me()
            AYIIN3.id = me.id
            AYIIN3.mention = me.mention
            AYIIN3.username = me.username
            if me.last_name:
                AYIIN3.name = me.first_name + " " + me.last_name
            else:
                AYIIN3.name = me.first_name
            #AYIIN3.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN3 in {AYIIN3.name} | [ {AYIIN3.id} ]"
            )
            client_id.append(AYIIN3.id)
        except Exception as e:
            logs.info(f"[STRING_3] ERROR: {e}")
    if AYIIN4:
        try:
            await AYIIN4.start()
            clients.append(4)
            await ayiin_client(AYIIN4)
            me = await AYIIN4.get_me()
            AYIIN4.id = me.id
            AYIIN4.mention = me.mention
            AYIIN4.username = me.username
            if me.last_name:
                AYIIN4.name = me.first_name + " " + me.last_name
            else:
                AYIIN4.name = me.first_name
            #AYIIN4.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN4 in {AYIIN4.name} | [ {AYIIN4.id} ]"
            )
            client_id.append(AYIIN4.id)
        except Exception as e:
            logs.info(f"[STRING_4] ERROR: {e}")
    if AYIIN5:
        try:
            await AYIIN5.start()
            clients.append(5)
            await ayiin_client(AYIIN5)
            me = await AYIIN5.get_me()
            AYIIN5.id = me.id
            AYIIN5.mention = me.mention
            AYIIN5.username = me.username
            if me.last_name:
                AYIIN5.name = me.first_name + " " + me.last_name
            else:
                AYIIN5.name = me.first_name
            #AYIIN5.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN5 in {AYIIN5.name} | [ {AYIIN5.id} ]"
            )
            client_id.append(AYIIN5.id)
        except Exception as e:
            logs.info(f"[STRING_5] ERROR: {e}")
    if AYIIN6:
        try:
            await AYIIN6.start()
            clients.append(6)
            await ayiin_client(AYIIN6)
            me = await AYIIN6.get_me()
            AYIIN6.id = me.id
            AYIIN6.mention = me.mention
            AYIIN6.username = me.username
            if me.last_name:
                AYIIN6.name = me.first_name + " " + me.last_name
            else:
                AYIIN6.name = me.first_name
            #AYIIN6.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN6 in {AYIIN6.name} | [ {AYIIN6.id} ]"
            )
            client_id.append(AYIIN6.id)
        except Exception as e:
            logs.info(f"[STRING_6] ERROR: {e}")
    if AYIIN7:
        try:
            await AYIIN7.start()
            clients.append(7)
            await ayiin_client(AYIIN7)
            me = await AYIIN7.get_me()
            AYIIN7.id = me.id
            AYIIN7.mention = me.mention
            AYIIN7.username = me.username
            if me.last_name:
                AYIIN7.name = me.first_name + " " + me.last_name
            else:
                AYIIN7.name = me.first_name
            #AYIIN7.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN7 in {AYIIN7.name} | [ {AYIIN7.id} ]"
            )
            client_id.append(AYIIN7.id)
        except Exception as e:
            logs.info(f"[STRING_7] ERROR: {e}")
    if AYIIN8:
        try:
            await AYIIN8.start()
            clients.append(8)
            await ayiin_client(AYIIN8)
            me = await AYIIN8.get_me()
            AYIIN8.id = me.id
            AYIIN8.mention = me.mention
            AYIIN8.username = me.username
            if me.last_name:
                AYIIN8.name = me.first_name + " " + me.last_name
            else:
                AYIIN8.name = me.first_name
            #AYIIN8.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN8 in {AYIIN8.name} | [ {AYIIN8.id} ]"
            )
            client_id.append(AYIIN8.id)
        except Exception as e:
            logs.info(f"[STRING_8] ERROR: {e}")
    if AYIIN9:
        try:
            await AYIIN9.start()
            clients.append(9)
            await ayiin_client(AYIIN9)
            me = await AYIIN9.get_me()
            AYIIN9.id = me.id
            AYIIN9.mention = me.mention
            AYIIN9.username = me.username
            if me.last_name:
                AYIIN9.name = me.first_name + " " + me.last_name
            else:
                AYIIN9.name = me.first_name
            #AYIIN9.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN9 in {AYIIN9.name} | [ {AYIIN9.id} ]"
            )
            client_id.append(AYIIN9.id)
        except Exception as e:
            logs.info(f"[STRING_9] ERROR: {e}")
    if AYIIN10:
        try:
            await AYIIN10.start()
            clients.append(10)
            await ayiin_client(AYIIN10)
            me = await AYIIN10.get_me()
            AYIIN10.id = me.id
            AYIIN10.mention = me.mention
            AYIIN10.username = me.username
            if me.last_name:
                AYIIN10.name = me.first_name + " " + me.last_name
            else:
                AYIIN10.name = me.first_name
            #AYIIN10.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN10 in {AYIIN10.name} | [ {AYIIN10.id} ]"
            )
            client_id.append(AYIIN10.id)
        except Exception as e:
            logs.info(f"[STRING_10] ERROR: {e}")
    if AYIIN11:
        try:
            await AYIIN11.start()
            clients.append(11)
            await ayiin_client(AYIIN11)
            me = await AYIIN11.get_me()
            AYIIN11.id = me.id
            AYIIN11.mention = me.mention
            AYIIN11.username = me.username
            if me.last_name:
                AYIIN11.name = me.first_name + " " + me.last_name
            else:
                AYIIN11.name = me.first_name
            #AYIIN11.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN11 in {AYIIN11.name} | [ {AYIIN11.id} ]"
            )
            client_id.append(AYIIN11.id)
        except Exception as e:
            logs.info(f"[STRING_11] ERROR: {e}")
    if AYIIN12:
        try:
            await AYIIN12.start()
            clients.append(12)
            await ayiin_client(AYIIN12)
            me = await AYIIN12.get_me()
            AYIIN12.id = me.id
            AYIIN12.mention = me.mention
            AYIIN12.username = me.username
            if me.last_name:
                AYIIN12.name = me.first_name + " " + me.last_name
            else:
                AYIIN12.name = me.first_name
            #AYIIN12.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN12 in {AYIIN12.name} | [ {AYIIN12.id} ]"
            )
            client_id.append(AYIIN12.id)
        except Exception as e:
            logs.info(f"[STRING_12] ERROR: {e}")
    if AYIIN13:
        try:
            await AYIIN13.start()
            clients.append(13)
            await ayiin_client(AYIIN13)
            me = await AYIIN13.get_me()
            AYIIN13.id = me.id
            AYIIN13.mention = me.mention
            AYIIN13.username = me.username
            if me.last_name:
                AYIIN13.name = me.first_name + " " + me.last_name
            else:
                AYIIN13.name = me.first_name
            #AYIIN13.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN13 in {AYIIN13.name} | [ {AYIIN13.id} ]"
            )
            client_id.append(AYIIN13.id)
        except Exception as e:
            logs.info(f"[STRING_13] ERROR: {e}")
    if AYIIN14:
        try:
            await AYIIN14.start()
            clients.append(14)
            await ayiin_client(AYIIN14)
            me = await AYIIN14.get_me()
            AYIIN14.id = me.id
            AYIIN14.mention = me.mention
            AYIIN14.username = me.username
            if me.last_name:
                AYIIN14.name = me.first_name + " " + me.last_name
            else:
                AYIIN14.name = me.first_name
            #AYIIN14.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN14 in {AYIIN14.name} | [ {AYIIN14.id} ]"
            )
            client_id.append(AYIIN14.id)
        except Exception as e:
            logs.info(f"[STRING_14] ERROR: {e}")
    if AYIIN15:
        try:
            await AYIIN15.start()
            clients.append(15)
            await ayiin_client(AYIIN15)
            me = await AYIIN5.get_me()
            AYIIN15.id = me.id
            AYIIN15.mention = me.mention
            AYIIN15.username = me.username
            if me.last_name:
                AYIIN15.name = me.first_name + " " + me.last_name
            else:
                AYIIN15.name = me.first_name
            #AYIIN15.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN15 in {AYIIN15.name} | [ {AYIIN15.id} ]"
            )
            client_id.append(AYIIN15.id)
        except Exception as e:
            logs.info(f"[STRING_15] ERROR: {e}")
    if AYIIN16:
        try:
            await AYIIN16.start()
            clients.append(16)
            await ayiin_client(AYIIN16)
            me = await AYIIN16.get_me()
            AYIIN16.id = me.id
            AYIIN16.mention = me.mention
            AYIIN16.username = me.username
            if me.last_name:
                AYIIN16.name = me.first_name + " " + me.last_name
            else:
                AYIIN16.name = me.first_name
            #AYIIN16.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN16 in {AYIIN16.name} | [ {AYIIN16.id} ]"
            )
            client_id.append(AYIIN16.id)
        except Exception as e:
            logs.info(f"[STRING_16] ERROR: {e}")
    if AYIIN17:
        try:
            await AYIIN17.start()
            clients.append(17)
            await ayiin_client(AYIIN17)
            me = await AYIIN17.get_me()
            AYIIN17.id = me.id
            AYIIN17.mention = me.mention
            AYIIN17.username = me.username
            if me.last_name:
                AYIIN17.name = me.first_name + " " + me.last_name
            else:
                AYIIN17.name = me.first_name
            #AYIIN17.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN17 in {AYIIN17.name} | [ {AYIIN17.id} ]"
            )
            client_id.append(AYIIN17.id)
        except Exception as e:
            logs.info(f"[STRING_17] ERROR: {e}")
    if AYIIN18:
        try:
            await AYIIN18.start()
            clients.append(18)
            await ayiin_client(AYIIN18)
            me = await AYIIN18.get_me()
            AYIIN18.id = me.id
            AYIIN18.mention = me.mention
            AYIIN18.username = me.username
            if me.last_name:
                AYIIN18.name = me.first_name + " " + me.last_name
            else:
                AYIIN18.name = me.first_name
            #AYIIN18.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN18 in {AYIIN18.name} | [ {AYIIN18.id} ]"
            )
            client_id.append(AYIIN18.id)
        except Exception as e:
            logs.info(f"[STRING_18] ERROR: {e}")
    if AYIIN19:
        try:
            await AYIIN19.start()
            clients.append(19)
            await ayiin_client(AYIIN19)
            me = await AYIIN19.get_me()
            AYIIN19.id = me.id
            AYIIN19.mention = me.mention
            AYIIN19.username = me.username
            if me.last_name:
                AYIIN19.name = me.first_name + " " + me.last_name
            else:
                AYIIN19.name = me.first_name
            #AYIIN19.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN19 in {AYIIN19.name} | [ {AYIIN19.id} ]"
            )
            client_id.append(AYIIN19.id)
        except Exception as e:
            logs.info(f"[STRING_19] ERROR: {e}")
    if AYIIN20:
        try:
            await AYIIN20.start()
            clients.append(20)
            await ayiin_client(AYIIN20)
            me = await AYIIN20.get_me()
            AYIIN20.id = me.id
            AYIIN20.mention = me.mention
            AYIIN20.username = me.username
            if me.last_name:
                AYIIN20.name = me.first_name + " " + me.last_name
            else:
                AYIIN20.name = me.first_name
            #AYIIN20.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN20 in {AYIIN20.name} | [ {AYIIN20.id} ]"
            )
            client_id.append(AYIIN20.id)
        except Exception as e:
            logs.info(f"[STRING_20] ERROR: {e}")
    if AYIIN21:
        try:
            await AYIIN21.start()
            clients.append(21)
            await ayiin_client(AYIIN21)
            me = await AYIIN21.get_me()
            AYIIN21.id = me.id
            AYIIN21.mention = me.mention
            AYIIN21.username = me.username
            if me.last_name:
                AYIIN21.name = me.first_name + " " + me.last_name
            else:
                AYIIN21.name = me.first_name
            #AYIIN21.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN21 in {AYIIN21.name} | [ {AYIIN21.id} ]"
            )
            client_id.append(AYIIN21.id)
        except Exception as e:
            logs.info(f"[STRING_21] ERROR: {e}")
    if AYIIN22:
        try:
            await AYIIN22.start()
            clients.append(22)
            await ayiin_client(AYIIN22)
            me = await AYIIN22.get_me()
            AYIIN22.id = me.id
            AYIIN22.mention = me.mention
            AYIIN22.username = me.username
            if me.last_name:
                AYIIN22.name = me.first_name + " " + me.last_name
            else:
                AYIIN22.name = me.first_name
            #AYIIN22.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN22 in {AYIIN22.name} | [ {AYIIN22.id} ]"
            )
            client_id.append(AYIIN22.id)
        except Exception as e:
            logs.info(f"[STRING_22] ERROR: {e}")
    if AYIIN23:
        try:
            await AYIIN23.start()
            clients.append(23)
            await ayiin_client(AYIIN23)
            me = await AYIIN23.get_me()
            AYIIN23.id = me.id
            AYIIN23.mention = me.mention
            AYIIN23.username = me.username
            if me.last_name:
                AYIIN23.name = me.first_name + " " + me.last_name
            else:
                AYIIN23.name = me.first_name
            #AYIIN23.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN23 in {AYIIN23.name} | [ {AYIIN23.id} ]"
            )
            client_id.append(AYIIN23.id)
        except Exception as e:
            logs.info(f"[STRING_23] ERROR: {e}")
    if AYIIN24:
        try:
            await AYIIN24.start()
            clients.append(24)
            await ayiin_client(AYIIN24)
            me = await AYIIN24.get_me()
            AYIIN24.id = me.id
            AYIIN24.mention = me.mention
            AYIIN24.username = me.username
            if me.last_name:
                AYIIN24.name = me.first_name + " " + me.last_name
            else:
                AYIIN24.name = me.first_name
            #AYIIN24.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN24 in {AYIIN24.name} | [ {AYIIN24.id} ]"
            )
            client_id.append(AYIIN24.id)
        except Exception as e:
            logs.info(f"[STRING_24] ERROR: {e}")
    if AYIIN25:
        try:
            await AYIIN25.start()
            clients.append(25)
            await ayiin_client(AYIIN25)
            me = await AYIIN25.get_me()
            AYIIN25.id = me.id
            AYIIN25.mention = me.mention
            AYIIN25.username = me.username
            if me.last_name:
                AYIIN25.name = me.first_name + " " + me.last_name
            else:
                AYIIN25.name = me.first_name
            #AYIIN25.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN25 in {AYIIN25.name} | [ {AYIIN25.id} ]"
            )
            client_id.append(AYIIN25.id)
        except Exception as e:
            logs.info(f"[STRING_25] ERROR: {e}")
    if AYIIN26:
        try:
            await AYIIN26.start()
            clients.append(26)
            await ayiin_client(AYIIN26)
            me = await AYIIN26.get_me()
            AYIIN26.id = me.id
            AYIIN26.mention = me.mention
            AYIIN26.username = me.username
            if me.last_name:
                AYIIN26.name = me.first_name + " " + me.last_name
            else:
                AYIIN26.name = me.first_name
            #AYIIN26.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN26 in {AYIIN26.name} | [ {AYIIN26.id} ]"
            )
            client_id.append(AYIIN26.id)
        except Exception as e:
            logs.info(f"[STRING_26] ERROR: {e}")
    if AYIIN27:
        try:
            await AYIIN27.start()
            clients.append(27)
            await ayiin_client(AYIIN27)
            me = await AYIIN27.get_me()
            AYIIN27.id = me.id
            AYIIN27.mention = me.mention
            AYIIN27.username = me.username
            if me.last_name:
                AYIIN27.name = me.first_name + " " + me.last_name
            else:
                AYIIN27.name = me.first_name
            #AYIIN27.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN27 in {AYIIN27.name} | [ {AYIIN27.id} ]"
            )
            client_id.append(AYIIN27.id)
        except Exception as e:
            logs.info(f"[STRING_27] ERROR: {e}")
    if AYIIN28:
        try:
            await AYIIN28.start()
            clients.append(28)
            await ayiin_client(AYIIN28)
            me = await AYIIN28.get_me()
            AYIIN28.id = me.id
            AYIIN28.mention = me.mention
            AYIIN28.username = me.username
            if me.last_name:
                AYIIN28.name = me.first_name + " " + me.last_name
            else:
                AYIIN28.name = me.first_name
            #AYIIN28.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN28 in {AYIIN28.name} | [ {AYIIN28.id} ]"
            )
            client_id.append(AYIIN28.id)
        except Exception as e:
            logs.info(f"[STRING_28] ERROR: {e}")
    if AYIIN29:
        try:
            await AYIIN29.start()
            clients.append(29)
            await ayiin_client(AYIIN29)
            me = await AYIIN29.get_me()
            AYIIN29.id = me.id
            AYIIN29.mention = me.mention
            AYIIN29.username = me.username
            if me.last_name:
                AYIIN29.name = me.first_name + " " + me.last_name
            else:
                AYIIN29.name = me.first_name
            #AYIIN29.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN19 in {AYIIN29.name} | [ {AYIIN29.id} ]"
            )
            client_id.append(AYIIN29.id)
        except Exception as e:
            logs.info(f"[STRING_29] ERROR: {e}")
    if AYIIN30:
        try:
            await AYIIN30.start()
            clients.append(30)
            await ayiin_client(AYIIN30)
            me = await AYIIN30.get_me()
            AYIIN30.id = me.id
            AYIIN30.mention = me.mention
            AYIIN30.username = me.username
            if me.last_name:
                AYIIN30.name = me.first_name + " " + me.last_name
            else:
                AYIIN30.name = me.first_name
            #AYIIN30.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN30 in {AYIIN30.name} | [ {AYIIN30.id} ]"
            )
            client_id.append(AYIIN30.id)
        except Exception as e:
            logs.info(f"[STRING_30] ERROR: {e}")
    if AYIIN31:
        try:
            await AYIIN31.start()
            clients.append(31)
            await ayiin_client(AYIIN31)
            me = await AYIIN31.get_me()
            AYIIN31.id = me.id
            AYIIN31.mention = me.mention
            AYIIN31.username = me.username
            if me.last_name:
                AYIIN31.name = me.first_name + " " + me.last_name
            else:
                AYIIN31.name = me.first_name
            #AYIIN31.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN31 in {AYIIN31.name} | [ {AYIIN31.id} ]"
            )
            client_id.append(AYIIN31.id)
        except Exception as e:
            logs.info(f"[STRING_31] ERROR: {e}")
    if AYIIN32:
        try:
            await AYIIN32.start()
            clients.append(32)
            await ayiin_client(AYIIN32)
            me = await AYIIN32.get_me()
            AYIIN32.id = me.id
            AYIIN32.mention = me.mention
            AYIIN32.username = me.username
            if me.last_name:
                AYIIN32.name = me.first_name + " " + me.last_name
            else:
                AYIIN32.name = me.first_name
            #AYIIN32.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN32 in {AYIIN32.name} | [ {AYIIN32.id} ]"
            )
            client_id.append(AYIIN32.id)
        except Exception as e:
            logs.info(f"[STRING_32] ERROR: {e}")
    if AYIIN33:
        try:
            await AYIIN33.start()
            clients.append(33)
            await ayiin_client(AYIIN33)
            me = await AYIIN33.get_me()
            AYIIN33.id = me.id
            AYIIN33.mention = me.mention
            AYIIN33.username = me.username
            if me.last_name:
                AYIIN33.name = me.first_name + " " + me.last_name
            else:
                AYIIN33.name = me.first_name
            #AYIIN33.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN33 in {AYIIN33.name} | [ {AYIIN33.id} ]"
            )
            client_id.append(AYIIN33.id)
        except Exception as e:
            logs.info(f"[STRING_33] ERROR: {e}")
    if AYIIN34:
        try:
            await AYIIN34.start()
            clients.append(34)
            await ayiin_client(AYIIN34)
            me = await AYIIN34.get_me()
            AYIIN34.id = me.id
            AYIIN34.mention = me.mention
            AYIIN34.username = me.username
            if me.last_name:
                AYIIN34.name = me.first_name + " " + me.last_name
            else:
                AYIIN34.name = me.first_name
            #AYIIN34.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN34 in {AYIIN34.name} | [ {AYIIN34.id} ]"
            )
            client_id.append(AYIIN34.id)
        except Exception as e:
            logs.info(f"[STRING_34] ERROR: {e}")
    if AYIIN35:
        try:
            await AYIIN35.start()
            clients.append(35)
            await ayiin_client(AYIIN35)
            me = await AYIIN35.get_me()
            AYIIN35.id = me.id
            AYIIN35.mention = me.mention
            AYIIN35.username = me.username
            if me.last_name:
                AYIIN35.name = me.first_name + " " + me.last_name
            else:
                AYIIN35.name = me.first_name
            #AYIIN35.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN35 in {AYIIN35.name} | [ {AYIIN35.id} ]"
            )
            client_id.append(AYIIN35.id)
        except Exception as e:
            logs.info(f"[STRING_35] ERROR: {e}")
    if AYIIN36:
        try:
            await AYIIN36.start()
            clients.append(36)
            await ayiin_client(AYIIN36)
            me = await AYIIN36.get_me()
            AYIIN36.id = me.id
            AYIIN36.mention = me.mention
            AYIIN36.username = me.username
            if me.last_name:
                AYIIN36.name = me.first_name + " " + me.last_name
            else:
                AYIIN36.name = me.first_name
            #AYIIN36.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN36 in {AYIIN36.name} | [ {AYIIN36.id} ]"
            )
            client_id.append(AYIIN36.id)
        except Exception as e:
            logs.info(f"[STRING_36] ERROR: {e}")
    if AYIIN37:
        try:
            await AYIIN37.start()
            clients.append(37)
            await ayiin_client(AYIIN37)
            me = await AYIIN37.get_me()
            AYIIN37.id = me.id
            AYIIN37.mention = me.mention
            AYIIN37.username = me.username
            if me.last_name:
                AYIIN37.name = me.first_name + " " + me.last_name
            else:
                AYIIN37.name = me.first_name
            #AYIIN37.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN37 in {AYIIN37.name} | [ {AYIIN37.id} ]"
            )
            client_id.append(AYIIN37.id)
        except Exception as e:
            logs.info(f"[STRING_37] ERROR: {e}")
    if AYIIN38:
        try:
            await AYIIN38.start()
            clients.append(38)
            await ayiin_client(AYIIN38)
            me = await AYIIN38.get_me()
            AYIIN38.id = me.id
            AYIIN38.mention = me.mention
            AYIIN38.username = me.username
            if me.last_name:
                AYIIN38.name = me.first_name + " " + me.last_name
            else:
                AYIIN38.name = me.first_name
            #AYIIN38.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN38 in {AYIIN38.name} | [ {AYIIN38.id} ]"
            )
            client_id.append(AYIIN38.id)
        except Exception as e:
            logs.info(f"[STRING_38] ERROR: {e}")
    if AYIIN39:
        try:
            await AYIIN39.start()
            clients.append(39)
            await ayiin_client(AYIIN39)
            me = await AYIIN39.get_me()
            AYIIN39.id = me.id
            AYIIN39.mention = me.mention
            AYIIN39.username = me.username
            if me.last_name:
                AYIIN39.name = me.first_name + " " + me.last_name
            else:
                AYIIN39.name = me.first_name
            #AYIIN39.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN39 in {AYIIN39.name} | [ {AYIIN39.id} ]"
            )
            client_id.append(AYIIN39.id)
        except Exception as e:
            logs.info(f"[STRING_39] ERROR: {e}")
    if AYIIN40:
        try:
            await AYIIN40.start()
            clients.append(40)
            await ayiin_client(AYIIN40)
            me = await AYIIN40.get_me()
            AYIIN40.id = me.id
            AYIIN40.mention = me.mention
            AYIIN40.username = me.username
            if me.last_name:
                AYIIN40.name = me.first_name + " " + me.last_name
            else:
                AYIIN40.name = me.first_name
            #AYIIN40.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN40 in {AYIIN40.name} | [ {AYIIN40.id} ]"
            )
            client_id.append(AYIIN40.id)
        except Exception as e:
            logs.info(f"[STRING_40] ERROR: {e}")
    if AYIIN41:
        try:
            await AYIIN41.start()
            clients.append(41)
            await ayiin_client(AYIIN41)
            me = await AYIIN41.get_me()
            AYIIN41.id = me.id
            AYIIN41.mention = me.mention
            AYIIN41.username = me.username
            if me.last_name:
                AYIIN41.name = me.first_name + " " + me.last_name
            else:
                AYIIN41.name = me.first_name
            #AYIIN41.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN41 in {AYIIN41.name} | [ {AYIIN41.id} ]"
            )
            client_id.append(AYIIN41.id)
        except Exception as e:
            logs.info(f"[STRING_41] ERROR: {e}")
    if AYIIN42:
        try:
            await AYIIN42.start()
            clients.append(42)
            await ayiin_client(AYIIN42)
            me = await AYIIN42.get_me()
            AYIIN42.id = me.id
            AYIIN42.mention = me.mention
            AYIIN42.username = me.username
            if me.last_name:
                AYIIN42.name = me.first_name + " " + me.last_name
            else:
                AYIIN42.name = me.first_name
            #AYIIN42.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN42 in {AYIIN42.name} | [ {AYIIN42.id} ]"
            )
            client_id.append(AYIIN42.id)
        except Exception as e:
            logs.info(f"[STRING_42] ERROR: {e}")
    if AYIIN43:
        try:
            await AYIIN43.start()
            clients.append(43)
            await ayiin_client(AYIIN43)
            me = await AYIIN43.get_me()
            AYIIN43.id = me.id
            AYIIN43.mention = me.mention
            AYIIN43.username = me.username
            if me.last_name:
                AYIIN43.name = me.first_name + " " + me.last_name
            else:
                AYIIN43.name = me.first_name
            #AYIIN43.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN43 in {AYIIN43.name} | [ {AYIIN43.id} ]"
            )
            client_id.append(AYIIN43.id)
        except Exception as e:
            logs.info(f"[STRING_43] ERROR: {e}")
    if AYIIN44:
        try:
            await AYIIN44.start()
            clients.append(44)
            await ayiin_client(AYIIN44)
            me = await AYIIN44.get_me()
            AYIIN44.id = me.id
            AYIIN44.mention = me.mention
            AYIIN44.username = me.username
            if me.last_name:
                AYIIN44.name = me.first_name + " " + me.last_name
            else:
                AYIIN44.name = me.first_name
            #AYIIN44.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN44 in {AYIIN44.name} | [ {AYIIN44.id} ]"
            )
            client_id.append(AYIIN44.id)
        except Exception as e:
            logs.info(f"[STRING_44] ERROR: {e}")
    if AYIIN45:
        try:
            await AYIIN45.start()
            clients.append(45)
            await ayiin_client(AYIIN45)
            me = await AYIIN45.get_me()
            AYIIN45.id = me.id
            AYIIN45.mention = me.mention
            AYIIN45.username = me.username
            if me.last_name:
                AYIIN45.name = me.first_name + " " + me.last_name
            else:
                AYIIN45.name = me.first_name
            #AYIIN45.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN45 in {AYIIN45.name} | [ {AYIIN45.id} ]"
            )
            client_id.append(AYIIN45.id)
        except Exception as e:
            logs.info(f"[STRING_45] ERROR: {e}")
    if AYIIN46:
        try:
            await AYIIN46.start()
            clients.append(46)
            await ayiin_client(AYIIN46)
            me = await AYIIN46.get_me()
            AYIIN46.id = me.id
            AYIIN46.mention = me.mention
            AYIIN46.username = me.username
            if me.last_name:
                AYIIN46.name = me.first_name + " " + me.last_name
            else:
                AYIIN46.name = me.first_name
            #AYIIN46.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN46 in {AYIIN46.name} | [ {AYIIN46.id} ]"
            )
            client_id.append(AYIIN46.id)
        except Exception as e:
            logs.info(f"[STRING_46] ERROR: {e}")
    if AYIIN47:
        try:
            await AYIIN47.start()
            clients.append(47)
            await ayiin_client(AYIIN47)
            me = await AYIIN47.get_me()
            AYIIN47.id = me.id
            AYIIN47.mention = me.mention
            AYIIN47.username = me.username
            if me.last_name:
                AYIIN47.name = me.first_name + " " + me.last_name
            else:
                AYIIN47.name = me.first_name
            #AYIIN47.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN47 in {AYIIN47.name} | [ {AYIIN47.id} ]"
            )
            client_id.append(AYIIN47.id)
        except Exception as e:
            logs.info(f"[STRING_47] ERROR: {e}")
    if AYIIN48:
        try:
            await AYIIN48.start()
            clients.append(48)
            await ayiin_client(AYIIN48)
            me = await AYIIN48.get_me()
            AYIIN48.id = me.id
            AYIIN48.mention = me.mention
            AYIIN48.username = me.username
            if me.last_name:
                AYIIN48.name = me.first_name + " " + me.last_name
            else:
                AYIIN48.name = me.first_name
            #AYIIN48.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN48 in {AYIIN48.name} | [ {AYIIN48.id} ]"
            )
            client_id.append(AYIIN48.id)
        except Exception as e:
            logs.info(f"[STRING_48] ERROR: {e}")
    if AYIIN49:
        try:
            await AYIIN49.start()
            clients.append(49)
            await ayiin_client(AYIIN49)
            me = await AYIIN49.get_me()
            AYIIN49.id = me.id
            AYIIN49.mention = me.mention
            AYIIN49.username = me.username
            if me.last_name:
                AYIIN49.name = me.first_name + " " + me.last_name
            else:
                AYIIN49.name = me.first_name
            #AYIIN49.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN49 in {AYIIN49.name} | [ {AYIIN49.id} ]"
            )
            client_id.append(AYIIN49.id)
        except Exception as e:
            logs.info(f"[STRING_49] ERROR: {e}")
    if AYIIN50:
        try:
            await AYIIN50.start()
            clients.append(50)
            await ayiin_client(AYIIN50)
            me = await AYIIN50.get_me()
            AYIIN50.id = me.id
            AYIIN50.mention = me.mention
            AYIIN50.username = me.username
            if me.last_name:
                AYIIN50.name = me.first_name + " " + me.last_name
            else:
                AYIIN50.name = me.first_name
            #AYIIN50.has_a_bot = True if tgbot else False
            logs.info(
                f"AYIIN45 in {AYIIN50.name} | [ {AYIIN50.id} ]"
            )
            client_id.append(AYIIN50.id)
        except Exception as e:
            logs.info(f"[STRING_50] ERROR: {e}")
    logs.info(
        f"Connect On [ {HOSTED_ON} ]\n"
    )
