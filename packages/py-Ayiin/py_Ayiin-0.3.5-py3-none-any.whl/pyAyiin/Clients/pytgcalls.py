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


from typing import Optional

from fipper.types import Message
from fipper.raw.functions.channels import GetFullChannel
from fipper.raw.functions.messages import GetFullChat
from fipper.raw.functions.phone import CreateGroupCall, DiscardGroupCall, EditGroupCallTitle
from fipper.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat

from ..methods.queue import Queues

from .client import *


class GroupCalls(Queues):
    def __init__(self):
        self.chat_id = []
        self.clients = {}
        self.active_calls = []
        self.msgid_cache = {}
        self.play_on = {}
    
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
