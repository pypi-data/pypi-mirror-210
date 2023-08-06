# py - Ayiin
# Copyright (C) 2022-2023 @AyiinXd
#
# This file is a part of < https://github.com/AyiinXd/pyAyiin >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/AyiinXd/pyAyiin/blob/main/LICENSE/>.
#
# FROM py-Ayiin <https://github.com/AyiinXd/pyAyiin>
# t.me/AyiinChat & t.me/AyiinSupport


# ========================×========================
#            Jangan Hapus Credit Ngentod
# ========================×========================

import asyncio
import os

from fipper.errors import FloodWait
from fipper.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    Message,
)


class FuncBot(object):
    async def approve_pmpermit(
        self,
        cb,
        user_ids,
        OLD_MSG,
    ):
        from ..dB.pmpermit import approve_pmpermit, is_pmpermit_approved

        
        if isinstance(cb, CallbackQuery):
            if await is_pmpermit_approved(user_ids):
                await cb.answer("Pengguna Ini Sudah Ada Di Database.", show_alert=True)
                return
            await approve_pmpermit(user_ids)
            await cb.edit_message_text("Pesan Anda Diterima Tod")
            if str(user_ids) in OLD_MSG:
                await OLD_MSG[str(user_ids)].delete()
        elif isinstance(cb, Message):
            if await is_pmpermit_approved(user_ids):
                await cb.edit("Pengguna Ini Sudah Ada Di Database.", show_alert=True)
                return
            await approve_pmpermit(user_ids)
            await cb.edit("Pesan Anda Diterima Tod")
            if str(user_ids) in OLD_MSG:
                await OLD_MSG[str(user_ids)].delete()
        
    async def disapprove_pmpermit(
        self,
        cb,
        user_ids,
    ):
        from ..dB.pmpermit import disapprove_pmpermit, is_pmpermit_approved
        
        if isinstance(cb, CallbackQuery):
            if not await is_pmpermit_approved(user_ids):
                return await cb.answer("Pengguna Ini Tidak Ada Di Database")
            await disapprove_pmpermit(user_ids)
            await cb.edit_message_text("Pesan Anda Ditolak Tod")
        elif isinstance(cb, Message):
            if not await is_pmpermit_approved(user_ids):
                return await cb.edit("Pengguna Ini Tidak Ada Di Database")
            await disapprove_pmpermit(user_ids)
            await cb.edit("Pesan Anda Ditolak Tod")


    async def logger(
        self,
        client,
        pepek,
    ):
        from pyAyiin.Clients.client import Var, tgbot

        if pepek.text:
            try:
                x = await tgbot.send_message(
                    Var.LOG_CHAT,
                    f"Logs: {client.me.first_name}\nPesan Dari: {pepek.from_user.first_name}\nPesan:\n{pepek.text}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("💌 Pengirim 💌", url=f"tg://openmessage?user_id={pepek.from_user.id}")],
                        ]
                    ),
                    disable_web_page_preview=True,
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BaseException:
                pass
        if pepek.photo:
            try:
                file = await client.download_media(pepek.photo)
                x = await tgbot.send_photo(
                    Var.LOG_CHAT,
                    photo=file,
                    caption=f"Logs: {client.me.first_name}\nPesan Dari: {pepek.from_user.first_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("💌 Pengirim 💌", url=f"tg://openmessage?user_id={pepek.from_user.id}")],
                        ]
                    ),
                )
                os.remove(file)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BaseException:
                pass
        if pepek.video:
            try:
                file = await client.download_media(pepek.video)
                x = await tgbot.send_video(
                    Var.LOG_CHAT,
                    video=file,
                    caption=f"Logs: {client.me.first_name}\nPesan Dari: {pepek.from_user.first_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("💌 Pengirim 💌", url=f"tg://openmessage?user_id={pepek.from_user.id}")],
                        ]
                    ),
                )
                os.remove(file)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BaseException:
                pass
        if pepek.voice:
            try:
                file = await client.download_media(pepek.voice)
                x = await tgbot.send_voice(
                    Var.LOG_CHAT,
                    voice=file,
                    caption=f"Logs: {client.me.first_name}\nPesan Dari: {pepek.from_user.first_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("💌 Pengirim 💌", url=f"tg://openmessage?user_id={pepek.from_user.id}")],
                        ]
                    ),
                )
                os.remove(file)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BaseException:
                pass
        if pepek.sticker:
            try:
                file = await client.download_media(pepek.sticker)
                x = await tgbot.send_sticker(
                    Var.LOG_CHAT,
                    sticker=file,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("💌 Pengirim 💌", url=f"tg://openmessage?user_id={pepek.from_user.id}")],
                        ]
                    ),
                )
                os.remove(file)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BaseException:
                pass
