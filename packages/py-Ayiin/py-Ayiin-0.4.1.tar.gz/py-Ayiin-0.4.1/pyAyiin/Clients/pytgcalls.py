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
import yt_dlp

from typing import Optional, Union

from fipper import Client
from fipper.types import Message
from fipper.raw.functions.channels import GetFullChannel
from fipper.raw.functions.messages import GetFullChat
from fipper.raw.functions.phone import CreateGroupCall, DiscardGroupCall, EditGroupCallTitle
from fipper.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat

from pytgcalls.exceptions import GroupCallNotFoundError

from ..methods.queue import Queues

from .client import *


ACTIVE_CALLS, QUEUE = [], {}
MSGID_CACHE, PLAY_ON = {}, {}
CLIENTS = {}


class GroupCalls(object):
    async def get_group_call(
        self,
        client: Client, 
        message: Message, 
        err_msg: str = "",
    ) -> Optional[InputGroupCall]:
        chat_peer = await client.resolve_peer(message.chat.id)
        if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
            if isinstance(chat_peer, InputPeerChannel):
                full_chat = (await client.invoke(GetFullChannel(channel=chat_peer))).full_chat
            elif isinstance(chat_peer, InputPeerChat):
                full_chat = (
                    await client.invoke(GetFullChat(chat_id=chat_peer.chat_id))
                ).full_chat
            if full_chat is not None:
                return full_chat.call
        await message.edit(f"<b>No group call Found</b> {err_msg}")
        return False
    
    async def TitleVc(self, client, m, title: str):
        peer = await client.resolve_peer(m.chat.id)
        if isinstance(peer, InputPeerChannel):
            chat = await client.invoke(GetFullChannel(channel=peer))
        if isinstance(peer, InputPeerChat):
            chat = await client.invoke(GetFullChat(chat_id=peer.chat_id))
        return await client.invoke(
            EditGroupCallTitle(
                call=chat.full_chat.call,
                title=title,
            )
        )

    async def StartVc(self, client, m, title=None):
        peer = await client.resolve_peer(m.chat.id)
        await client.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=client.rnd_id() // 9000000000,
            )
        )
        titt = title if title else "🎧 Ayiin Music 🎧"
        await self.TitleVc(client, m, title=titt)

    async def StopVc(
        self,
        client,
        message,
    ):
        group_call = await self.get_group_call(client, message, err_msg="group call already ended")
        if not group_call:
            return
        await client.invoke(DiscardGroupCall(call=group_call))


class VcMusic(Queues):
    def __init__(self, client: Client, message: Message):
        self.m = message
        self.chat_id = []
        self.clients = {}
        self.client = client
        self.active_calls = []
        self.msgid_cache = {}
        self.play_on = {}

    async def startCall(self):
        if PLAY_ON:
            for chats in PLAY_ON:
                await PLAY_ON[chats].stop()
            PLAY_ON.clear()
            await asyncio.sleep(3)
        if self.m.video:
            for chats in list(CLIENTS):
                if chats != self.m.chat.id:
                    await CLIENTS[chats].stop()
                    del CLIENTS[chats]
            PLAY_ON.update({self._chat: self.client.group_call})
        if self.m.chat.id not in ACTIVE_CALLS:
            try:
                self.client.group_call.on_network_status_changed(
                    self.on_network_changed)
                self.client.group_call.on_playout_ended(self.playout_ended_handler)
                await self.client.group_call.join(self.m.chat.id)
            except GroupCallNotFoundError as er:
                await self.m.reply(er)
                dn, err = await self.StartVc()
                if err:
                    return False, err
            except Exception as e:
                await self.m.reply(e)
                return False, e
        return True, None

    async def on_network_changed(self, call, is_connected):
        chat = self.m.chat.id
        if is_connected:
            if chat not in ACTIVE_CALLS:
                ACTIVE_CALLS.append(chat)
        elif chat in ACTIVE_CALLS:
            ACTIVE_CALLS.remove(chat)

    async def playout_ended_handler(self, call, source, mtype):
        if os.path.exists(source):
            os.remove(source)
        await self.play_from_queue()

    async def play_from_queue(self):
        chat_id = self.m.chat.id
        if chat_id in PLAY_ON:
            await self.client.group_call.stop_video()
            PLAY_ON.pop(chat_id)
        try:
            ppk = await self.skip_song(self.client, chat_id)
            if ppk == 0:
                await self.client.group_call.leave()
            elif ppk == 1:
                await self.m.reply("<b>Antrian Udah Kosong Tod, Gua Cabut Dari OS</b>")
            else:
                await self.m.reply(
                    f"<b>• Memutar</b> - <a href='{ppk[1]}'>{ppk[0]}</a> | <code>{ppk[2]}</code>\n• <b>Pengguna:</b> {self.client.me.mention}",
                    disable_web_page_preview=True,
                )
        except Exception as e:
            await self.m.reply(e)


    async def JoinVc(self):
        chat_id = self.m.chat.id
        done, err = await self.startCall()

        if done:
            return True
        await self.client.send_message(
            self.m.chat.id,
            f"KESALAHAN saat Bergabung ke Obrolan Suara - {chat_id} :\n{err}",
        )
        return False
