# AyiinXd
# Copyright (C) 2022-2023 @AyiinXd
#
# This file is a part of < https://github.com/AyiinXd/AyiinXd >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/AyiinXd/AyiinXd/blob/main/LICENSE/>.
#
# FROM AyiinXd <https://github.com/AyiinXd/AyiinXd>
# t.me/AyiinChat & t.me/AyiinSupport


# ========================×========================
#            Jangan Hapus Credit Ngentod
# ========================×========================

import aiohttp
import asyncio
import base64
import importlib
import math
import os
import shlex
import textwrap
from aiohttp import ContentTypeError
from typing import Tuple, Union
from io import BytesIO

from pymediainfo import MediaInfo
from fipper import Client, enums, raw
from fipper.types import Message, User
from PIL import Image, ImageDraw, ImageFont


_entitie = {
    raw.types.MessageEntityPhone: "phone_number",
    raw.types.MessageEntityMention: "mention",
    raw.types.MessageEntityBold: "bold",
    raw.types.MessageEntityCashtag: "cashtag",
    raw.types.MessageEntityStrike: "strikethrough",
    raw.types.MessageEntityHashtag: "hashtag",
    raw.types.MessageEntityEmail: "email",
    raw.types.MessageEntityMentionName: "text_mention",
    raw.types.MessageEntityUnderline: "underline",
    raw.types.MessageEntityUrl: "url",
    raw.types.MessageEntityTextUrl: "text_link",
    raw.types.MessageEntityBotCommand: "bot_command",
    raw.types.MessageEntityCode: "code",
    raw.types.MessageEntityPre: "pre",
}

class Function(object):
    def __init__(self):
        self._entities = _entitie
        self.o_api = "https://bot.lyo.su/quote/generate"
    
    
    async def get_readable_time(self, seconds: int) -> str:
        count = 0
        up_time = ""
        time_list = []
        time_suffix_list = ["s", "m", "Jam", "Hari"]
    
        while count < 4:
            count += 1
            remainder, result = divmod(
                seconds, 60) if count < 3 else divmod(
                seconds, 24)
            if seconds == 0 and remainder == 0:
                break
            time_list.append(int(result))
            seconds = int(remainder)
    
        for x in range(len(time_list)):
            time_list[x] = str(time_list[x]) + time_suffix_list[x]
        if len(time_list) == 4:
            up_time += time_list.pop() + ", "
    
        time_list.reverse()
        up_time += ":".join(time_list)
    
        return up_time
    
    
    async def add_text_img(
        self,
        image_path,
        text,
        fonts,
    ):
        font_size = 12
        stroke_width = 1
    
        if ";" in text:
            upper_text, lower_text = text.split(";")
        else:
            upper_text = text
            lower_text = ""
    
        img = Image.open(image_path).convert("RGBA")
        img_info = img.info
        image_width, image_height = img.size
        font = ImageFont.truetype(
            font=fonts,
            size=int(image_height * font_size) // 100,
        )
        draw = ImageDraw.Draw(img)
    
        char_width, char_height = font.getsize("A")
        chars_per_line = image_width // char_width
        top_lines = textwrap.wrap(upper_text, width=chars_per_line)
        bottom_lines = textwrap.wrap(lower_text, width=chars_per_line)
    
        if top_lines:
            y = 10
            for line in top_lines:
                line_width, line_height = font.getsize(line)
                x = (image_width - line_width) / 2
                draw.text(
                    (x, y),
                    line,
                    fill="white",
                    font=font,
                    stroke_width=stroke_width,
                    stroke_fill="black",
                )
                y += line_height
    
        if bottom_lines:
            y = image_height - char_height * len(bottom_lines) - 15
            for line in bottom_lines:
                line_width, line_height = font.getsize(line)
                x = (image_width - line_width) / 2
                draw.text(
                    (x, y),
                    line,
                    fill="white",
                    font=font,
                    stroke_width=stroke_width,
                    stroke_fill="black",
                )
                y += line_height
    
        final_image = os.path.join("memify.webp")
        img.save(final_image, **img_info)
        return final_image


# https://github.com/TeamUltroid/pyUltroid/blob/31c271cf4d35ab700e5880e952e54c82046812c2/pyUltroid/functions/helper.py#L154


    async def bash(self, cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        err = stderr.decode().strip()
        out = stdout.decode().strip()
        return out, err
    
    
    async def run_cmd(self, cmd: str) -> Tuple[str, str, int, int]:
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )
    
    
    # PyroHelper
    
    
    async def get_ub_chats(
        self,
        client,
        chat_types: list = [
            enums.ChatType.GROUP,
            enums.ChatType.SUPERGROUP,
            enums.ChatType.CHANNEL,
        ],
        is_id_only=True,
    ):
        ub_chats = []
        async for dialog in client.get_dialogs():
            if dialog.chat.type in chat_types:
                if is_id_only:
                    ub_chats.append(dialog.chat.id)
                else:
                    ub_chats.append(dialog.chat)
            else:
                continue
        return ub_chats
    
    
    def ReplyCheck(self, message: Message):
        reply_id = None
    
        if message.reply_to_message:
            reply_id = message.reply_to_message.id
    
        elif message.from_user.is_self:
            reply_id = message.id
    
        return reply_id
    
    
    def SpeedConvert(self, size):
        power = 2**10
        zero = 0
        units = {0: "", 1: "Kbit/s", 2: "Mbit/s", 3: "Gbit/s", 4: "Tbit/s"}
        while size > power:
            size /= power
            zero += 1
        return f"{round(size, 2)} {units[zero]}"
    
    
    def GetFromUserID(self, message: Message):
        """Get the user id of the incoming message."""
        return message.from_user.id
    
    
    def GetChatID(self, message: Message):
        """Get the group id of the incoming message"""
        return message.chat.id
    
    
    def GetUserMentionable(self, user: User):
        """Get mentionable text of a user."""
        if user.username:
            username = "@{}".format(user.username)
        else:
            if user.last_name:
                name_string = "{} {}".format(user.first_name, user.last_name)
            else:
                name_string = "{}".format(user.first_name)
    
            username = "<a href='tg://user?id={}'>{}</a>".format(
                user.id, name_string)
    
        return username
    
    
    async def async_searcher(
        self,
        url: str,
        post: bool = None,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        data: dict = None,
        ssl=None,
        re_json: bool = False,
        re_content: bool = False,
        real: bool = False,
    ):
        async with aiohttp.ClientSession(headers=headers) as client:
            if post:
                data = await client.post(url, json=json, data=data, ssl=ssl)
            else:
                data = await client.get(url, params=params, ssl=ssl)
            if re_json:
                return await data.json()
            if re_content:
                return await data.read()
            if real:
                return data
            return await data.text()
    
    
    async def _format_quote(self, message, reply=None, sender=None, type_="private"):
        from pyAyiin import DEVS
        
        
        async def telegraph(self, file_):
            file = f"{file_}.png"
            Image.open(file_).save(file, "PNG")
            files = {"file": open(file, "rb").read()}
            uri = (
                "https://telegra.ph"
                + (
                    await self.async_searcher(
                        "https://telegra.ph/upload", post=True, data=files, re_json=True
                    )
                )[0]["src"]
            )
            os.remove(file)
            os.remove(file_)
            return uri

        if reply:
            reply = {
                "name": reply.from_user.first_name or "Deleted Account",
                "text": reply.text,
                "chatId": reply.chat.id,
            }
        else:
            reply = {}
        is_fwd = message.from_user
        name = None
        last_name = None
        if sender and sender.id not in DEVS:
            id_ = sender.id
            name = sender.first_name
        elif not is_fwd:
            id_ = message.from_user.id
            sender = message.from_user
            name = message.from_user.first_name
        else:
            id_, sender = None, None
            name = is_fwd.first_name
            if is_fwd.id:
                try:
                    id_ = is_fwd.id
                    sender = await message._client.get_users(id_)
                    name = sender.first_name
                except ValueError:
                    pass
        if sender and hasattr(sender, "last_name"):
            last_name = sender.last_name
        entities = []
        if message.entities:
            for entity in message.entities:
                if type(entity) in self._entities:
                    enti_ = entity.to_dict()
                    del enti_["_"]
                    enti_["type"] = self._entities[type(entity)]
                    entities.append(enti_)
        message = {
            "entities": entities,
            "chatId": id_,
            "avatar": True,
            "from": {
                "id": id_,
                "first_name": (name or (sender.first_name if sender else None))
                or "Deleted Account",
                "last_name": last_name,
                "username": sender.username if sender else None,
                "language_code": "en",
                "title": name,
                "name": name or "Unknown",
                "type": type_,
            },
            "text": message.text,
            "replyMessage": {},
        }

        return message


    async def create_quotly(
        self,
        message,
        url="https://qoute-api-akashpattnaik.koyeb.app/generate",
        reply={},
        bg=None,
        sender=None,
        file_name="quote.webp",
    ):
        if not isinstance(message, list):
            message = [message]
            url = self.o_api
        if not bg:
            bg = "#1b1429"
        content = {
            "type": "quote",
            "format": "webp",
            "backgroundColor": bg,
            "width": 512,
            "height": 768,
            "scale": 2,
            "messages": [
                await self._format_quote(msg, reply=reply, sender=sender)
                for msg in message
            ],
        }
        try:
            request = await self.async_searcher(url, post=True, json=content, re_json=True)
        except ContentTypeError as er:
            if url != self.o_api:
                return await self.create_quotly(
                    message,
                    url=self.o_api,
                    bg=bg,
                    sender=sender,
                    reply=reply,
                    file_name=file_name,
                )
            raise er
        if request.get("ok"):
            with open(file_name, "wb") as file:
                image = base64.decodebytes(
                    request["result"]["image"].encode("utf-8"))
                file.write(image)
            return file_name
        raise Exception(str(request))
    
    
    async def Carbon(
        self,
        code,
        base_url="https://carbonara-42.herokuapp.com/api/cook",
        file_name="Ayiin-Ubot",
        **kwargs,
    ):
        kwargs["code"] = code
        con = await self.async_searcher(base_url, post=True, json=kwargs, re_content=True)
        file = BytesIO(con)
        file.name = f"{file_name}.jpg"
        return file
    
    
    def humanbytes(self, size: Union[int, float]) -> str:
        if size is None or isinstance(size, str):
            return ""
    
        power = 2**10
        raised_to_pow = 0
        dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
        while size > power:
            size /= power
            raised_to_pow += 1
        return f"{str(round(size, 2))} {dict_power_n[raised_to_pow]}B"
