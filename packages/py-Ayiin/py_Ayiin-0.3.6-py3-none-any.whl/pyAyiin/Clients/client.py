from pyrogram import Client as PyroClient
from fipper import Client

from telethon import TelegramClient
from telethon.sessions import MemorySession

from . import *

from ..config import Var as Variable

Var = Variable()


hndlr = f"{Var.HNDLR[0]} {Var.HNDLR[1]} {Var.HNDLR[2]} {Var.HNDLR[3]} {Var.HNDLR[4]} {Var.HNDLR[5]}"



TeleBot = TelegramClient(
    MemorySession(), 
    Var.API_ID, 
    Var.API_HASH
)

tgbot = (
    Client(
        name="tgbot",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN,
    )
)


# For Publik Repository
AYIIN1 = (
    Client(
        name="AYIIN1",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_1,
        in_memory=True,
    )
    if Var.STRING_1
    else None
)

AYIIN2 = (
    Client(
        name="AYIIN2",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_2,
        in_memory=True,
    )
    if Var.STRING_2
    else None
)
        
AYIIN3 = (
    Client(
        name="AYIIN3",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_3,
        in_memory=True,
    )
    if Var.STRING_3
    else None
)

AYIIN4 = (
    Client(
        name="AYIIN4",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_4,
        in_memory=True,
    )
    if Var.STRING_4
    else None
)

AYIIN5 = (
    Client(
        name="AYIIN5",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_5,
        in_memory=True,
    )
    if Var.STRING_5
    else None
)

AYIIN6 = (
    Client(
        name="AYIIN6",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_6,
        in_memory=True,
    )
    if Var.STRING_6
    else None
)


AYIIN7 = (
    Client(
        name="AYIIN7",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_7,
        in_memory=True,
    )
    if Var.STRING_7
    else None
)
        
AYIIN8 = (
    Client(
        name="AYIIN8",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_8,
        in_memory=True,
    )
    if Var.STRING_8
    else None
)


AYIIN9 = (
    Client(
        name="AYIIN9",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_9,
        in_memory=True,
    )
    if Var.STRING_9
    else None
)
AYIIN10 = (
    Client(
        name="AYIIN10",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.STRING_10,
        in_memory=True,
    )
    if Var.STRING_10
    else None
)

AYIIN11 = (
    Client(
        name="AYIIN11",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_11,
        in_memory=True,
    )
    if Var.SESSION_11
    else None
)

AYIIN12 = (
    Client(
        name="AYIIN12",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_12,
        in_memory=True,
    )
    if Var.SESSION_12
    else None
)

AYIIN13 = (
    Client(
        name="AYIIN13",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_13,
        in_memory=True,
    )
    if Var.SESSION_13
    else None
)

AYIIN14 = (
    Client(
        name="AYIIN14",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_14,
        in_memory=True,
    )
    if Var.SESSION_14
    else None
)

AYIIN15 = (
    Client(
        name="AYIIN15",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_15,
        in_memory=True,
    )
    if Var.SESSION_15
    else None
)

AYIIN16 = (
    Client(
        name="AYIIN16",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_16,
        in_memory=True,
    )
    if Var.SESSION_16
    else None
)

AYIIN17 = (
    Client(
        name="AYIIN17",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_17,
        in_memory=True,
    )
    if Var.SESSION_17
    else None
)

AYIIN18 = (
    Client(
        name="AYIIN18",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_18,
        in_memory=True,
    )
    if Var.SESSION_18
    else None
)

AYIIN19 = (
    Client(
        name="AYIIN19",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_19,
        in_memory=True,
    )
    if Var.SESSION_19
    else None
)

AYIIN20 = (
    Client(
        name="AYIIN20",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_20,
        in_memory=True,
    )
    if Var.SESSION_20
    else None
)

AYIIN21 = (
    Client(
        name="AYIIN21",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_21,
        in_memory=True,
    )
    if Var.SESSION_21
    else None
)

AYIIN22 = (
    Client(
        name="AYIIN22",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_22,
        in_memory=True,
    )
    if Var.SESSION_22
    else None
)

AYIIN23 = (
    Client(
        name="AYIIN23",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_23,
        in_memory=True,
    )
    if Var.SESSION_23
    else None
)

AYIIN24 = (
    Client(
        name="AYIIN24",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_24,
        in_memory=True,
    )
    if Var.SESSION_24
    else None
)

AYIIN25 = (
    Client(
        name="AYIIN25",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_25,
        in_memory=True,
    )
    if Var.SESSION_25
    else None
)

AYIIN26 = (
    Client(
        name="AYIIN26",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_26,
        in_memory=True,
    )
    if Var.SESSION_26
    else None
)

AYIIN27 = (
    Client(
        name="AYIIN27",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_27,
        in_memory=True,
    )
    if Var.SESSION_27
    else None
)

AYIIN28 = (
    Client(
        name="AYIIN28",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_28,
        in_memory=True,
    )
    if Var.SESSION_28
    else None
)

AYIIN29 = (
    Client(
        name="AYIIN29",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_29,
        in_memory=True,
    )
    if Var.SESSION_29
    else None
)

AYIIN30 = (
    Client(
        name="AYIIN30",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_30,
        in_memory=True,
    )
    if Var.SESSION_30
    else None
)

AYIIN31 = (
    Client(
        name="AYIIN31",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_31,
        in_memory=True,
    )
    if Var.SESSION_31
    else None
)

AYIIN32 = (
    Client(
        name="AYIIN32",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_32,
        in_memory=True,
    )
    if Var.SESSION_32
    else None
)

AYIIN33 = (
    Client(
        name="AYIIN33",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_33,
        in_memory=True,
    )
    if Var.SESSION_33
    else None
)

AYIIN34 = (
    Client(
        name="AYIIN34",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_34,
        in_memory=True,
    )
    if Var.SESSION_34
    else None
)

AYIIN35 = (
    Client(
        name="AYIIN35",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_35,
        in_memory=True,
    )
    if Var.SESSION_35
    else None
)

AYIIN36 = (
    Client(
        name="AYIIN36",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_36,
        in_memory=True,
    )
    if Var.SESSION_36
    else None
)

AYIIN37 = (
    Client(
        name="AYIIN37",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_37,
        in_memory=True,
    )
    if Var.SESSION_37
    else None
)

AYIIN38 = (
    Client(
        name="AYIIN38",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_38,
        in_memory=True,
    )
    if Var.SESSION_38
    else None
)

AYIIN39 = (
    Client(
        name="AYIIN39",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_39,
        in_memory=True,
    )
    if Var.SESSION_39
    else None
)

AYIIN40 = (
    Client(
        name="AYIIN40",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_40,
        in_memory=True,
    )
    if Var.SESSION_40
    else None
)

AYIIN41 = (
    Client(
        name="AYIIN41",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_41,
        in_memory=True,
    )
    if Var.SESSION_41
    else None
)

AYIIN42 = (
    Client(
        name="AYIIN42",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_42,
        in_memory=True,
    )
    if Var.SESSION_42
    else None
)

AYIIN43 = (
    Client(
        name="AYIIN43",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_43,
        in_memory=True,
    )
    if Var.SESSION_43
    else None
)

AYIIN44 = (
    Client(
        name="AYIIN44",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_44,
        in_memory=True,
    )
    if Var.SESSION_44
    else None
)

AYIIN45 = (
    Client(
        name="AYIIN45",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_45,
        in_memory=True,
    )
    if Var.SESSION_45
    else None
)

AYIIN46 = (
    Client(
        name="AYIIN46",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_46,
        in_memory=True,
    )
    if Var.SESSION_46
    else None
)

AYIIN47 = (
    Client(
        name="AYIIN47",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_47,
        in_memory=True,
    )
    if Var.SESSION_47
    else None
)

AYIIN48 = (
    Client(
        name="AYIIN48",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_48,
        in_memory=True,
    )
    if Var.SESSION_48
    else None
)

AYIIN49 = (
    Client(
        name="AYIIN49",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_49,
        in_memory=True,
    )
    if Var.SESSION_49
    else None
)

AYIIN50 = (
    Client(
        name="AYIIN50",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        session_string=Var.SESSION_50,
        in_memory=True,
    )
    if Var.SESSION_50
    else None
)


Bots = [
    bot for bot in [
        AYIIN1, 
        AYIIN2, 
        AYIIN3, 
        AYIIN4, 
        AYIIN5, 
        AYIIN6, 
        AYIIN7, 
        AYIIN8,
        AYIIN9,
        AYIIN10,
        AYIIN11,
        AYIIN12,
        AYIIN13,
        AYIIN14,
        AYIIN15,
        AYIIN16,
        AYIIN17,
        AYIIN18,
        AYIIN19,
        AYIIN20,
        AYIIN21,
        AYIIN22,
        AYIIN23,
        AYIIN24,
        AYIIN25,
        AYIIN26,
        AYIIN27,
        AYIIN28,
        AYIIN29,
        AYIIN30,
        AYIIN31,
        AYIIN32,
        AYIIN33,
        AYIIN34,
        AYIIN35,
        AYIIN36,
        AYIIN37,
        AYIIN38,
        AYIIN39,
        AYIIN40,
        AYIIN41,
        AYIIN42,
        AYIIN43,
        AYIIN44,
        AYIIN45,
        AYIIN46,
        AYIIN47,
        AYIIN48,
        AYIIN49,
        AYIIN50,
    ] if bot
]
