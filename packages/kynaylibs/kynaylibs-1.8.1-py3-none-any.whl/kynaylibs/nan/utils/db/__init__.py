import asyncio
import codecs
import pickle
from datetime import datetime, timedelta
from platform import python_version as py
from typing import Dict, List, Union

import pymongo.errors
import requests
from dateutil.relativedelta import relativedelta
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from naya import *
from naya.config import *
from pyrogram import Client
from pyrogram import __version__ as pyro
from pyrogram import filters
from pyrogram.filters import chat
from pyrogram.types import Message

from kynaylibs.version import __version__ as nay
from kynaylibs.version import kynay_version as nan

mongo = MongoCli(MONGO_URL)
db = mongo.premium
ubotdb = db.ubot
coupledb = db.couple
notesdb = db.notes
filtersdb = db.filters
accesdb = db.acces
usersdb = db.users
logdb = db.gruplog
blchatdb = db.blchat
pmdb = db.pmpermit
afkdb = db.afk
resell = db.seles
expdb = db.expired
sudoersdb = db.sudoers

MSG_ON = """
**Naya Premium Actived ✅**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
◉ **Versi** : `{}`
◉ **Phython** : `{}`
◉ **Pyrogram** : `{}`
**Ketik** `{}alive` **untuk Mengecheck Bot**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
"""

MSG_ON2 = """
**Naya Premium Actived ✅**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
◉ **Versi** : `{}`
◉ **Phython** : `{}`
◉ **Pyrogram** : `{}`
**Ketik** `{}alive` **untuk Mengecheck Bot**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
"""


async def buat_log():
    botlog_chat_id = None
    for _bots in await get_userbots():
        bots_ = Ubot(**_bots)
    try:
        if bots_.is_connected:
            await bots_.disconnect()
        else:
            bots_.in_memory = False
            await bots_.start()
        try:
            user = await bots_.get_me()
            user_id = user.id
            user_data = await usersdb.users.find_one({"user_id": user_id})
            botlog_chat_id = None

            if user_data:
                botlog_chat_id = user_data.get("bot_log_group_id")

            if not user_data or not botlog_chat_id:
                group_name = "Naya Premium Logs"
                group_description = "Jangan Hapus Atau Keluar Dari Grup Ini\n\nCreated By @KynanSupport .\nJika menemukan kendala atau ingin menanyakan sesuatu\nHubungi : @kenapanan, @rizzvbss atau bisa ke @KynanSupport."
                group = await bots_.create_supergroup(group_name, group_description)
                botlog_chat_id = group.id
                photo = "naya/resources/logo.jpg"
                await bots_.set_chat_photo(botlog_chat_id, photo=photo)
                message_text = (
                    f"Grup Log Berhasil Dibuat,\nJangan keluar dari grup log ini.\n"
                )
                await set_botlog(user_id, botlog_chat_id)
                await asyncio.sleep(1)
                await bots_.send_message(botlog_chat_id, message_text)
                await asyncio.sleep(1)
                await usersdb.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"bot_log_group_id": botlog_chat_id}},
                    upsert=True,
                )
        except Exception as a:
            LOGGER("Info").info(f"{a}")

    except Exception as e:
        LOGGER("X").info(f"{e}")

    if botlog_chat_id is None:
        return None

    return int(botlog_chat_id)


async def babi(bot):
    user = await bot.get_me()
    user_id = user.id
    user_data = await usersdb.users.find_one({"user_id": user_id})
    botlog_chat_id = None

    if user_data:
        botlog_chat_id = user_data.get("bot_log_group_id")

    if not user_data or not botlog_chat_id:
        group_name = "Naya Premium Logs"
        group_description = "Jangan Hapus Atau Keluar Dari Grup Ini\n\nCreated By @KynanSupport .\nJika menemukan kendala atau ingin menanyakan sesuatu\nHubungi : @kenapanan, @rizzvbss atau bisa ke @KynanSupport."
        group = await bot.create_supergroup(group_name, group_description)
        botlog_chat_id = group.id
        photo = "naya/resources/logo.jpg"
        await bot.set_chat_photo(botlog_chat_id, photo=photo)
        message_text = f"Grup Log Berhasil Dibuat,\nKetik `{cmd}setlog` untuk menentapkan grup log ini sebagai tempat log bot\n"
        await set_botlog(user_id, botlog_chat_id)
        await asyncio.sleep(1)
        await bot.send_message(botlog_chat_id, MSG_ON2.format(nan, py(), pyro, cmd))
        await asyncio.sleep(1)

        await usersdb.users.update_one(
            {"user_id": user_id},
            {"$set": {"bot_log_group_id": botlog_chat_id}},
            upsert=True,
        )

    if botlog_chat_id is None:
        return None

    return int(botlog_chat_id)


async def get_botlog(user_id: int):
    user_data = await logdb.users.find_one({"user_id": user_id})
    botlog_chat_id = user_data.get("bot_log_group_id") if user_data else None
    return botlog_chat_id


async def set_botlog(user_id: int, botlog_chat_id: int):
    await logdb.users.update_one(
        {"user_id": user_id},
        {"$set": {"bot_log_group_id": botlog_chat_id}},
        upsert=True,
    )


async def get_log_groups(user_id: int):
    user_data = await logdb.users.find_one({"user_id": user_id})
    botlog_chat_id = user_data.get("bot_log_group_id") if user_data else []
    return botlog_chat_id


async def _get_lovers(chat_id: int):
    lovers = await coupledb.find_one({"chat_id": chat_id})
    if lovers:
        lovers = lovers["couple"]
    else:
        lovers = {}
    return lovers


async def get_couple(chat_id: int, date: str):
    lovers = await _get_lovers(chat_id)
    if date in lovers:
        return lovers[date]
    else:
        return False


async def save_couple(chat_id: int, date: str, couple: dict):
    lovers = await _get_lovers(chat_id)
    lovers[date] = couple
    await coupledb.update_one(
        {"chat_id": chat_id},
        {"$set": {"couple": lovers}},
        upsert=True,
    )


async def get_notes_count() -> dict:
    chats_count = 0
    notes_count = 0
    async for chat in notesdb.find({"user_id": {"$exists": 1}}):
        notes_name = await get_note_names(chat["user_id"])
        notes_count += len(notes_name)
        chats_count += 1
    return {"chats_count": chats_count, "notes_count": notes_count}


async def _get_notes(user_id: int) -> Dict[str, int]:
    _notes = await notesdb.find_one({"user_id": user_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_note_names(user_id: int) -> List[str]:
    _notes = []
    for note in await _get_notes(user_id):
        _notes.append(note)
    return _notes


async def get_note(user_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _notes = await _get_notes(user_id)
    if name in _notes:
        return _notes[name]
    return False


async def save_note(user_id: int, name: str, note: dict):
    name = name.lower().strip()
    _notes = await _get_notes(user_id)
    _notes[name] = note

    await notesdb.update_one(
        {"user_id": user_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_note(user_id: int, name: str) -> bool:
    notesd = await _get_notes(user_id)
    name = name.lower().strip()
    if name in notesd:
        del notesd[name]
        await notesdb.update_one(
            {"user_id": user_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


def obj_to_str(obj):
    if not obj:
        return False
    string = codecs.encode(pickle.dumps(obj), "base64").decode()
    return string


def str_to_obj(string: str):
    obj = pickle.loads(codecs.decode(string.encode(), "base64"))
    return obj


async def get_filters_count() -> dict:
    chats_count = 0
    filters_count = 0
    async for chat in filtersdb.find({"chat_id": {"$lt": 0}}):
        filters_name = await get_filters_names(chat["chat_id"])
        filters_count += len(filters_name)
        chats_count += 1
    return {
        "chats_count": chats_count,
        "filters_count": filters_count,
    }


async def _get_filters(user_id: int, chat_id: int) -> Dict[str, int]:
    _filters = await filtersdb.find_one({"user_id": user_id, "chat_id": chat_id})
    if not _filters:
        return {}
    return _filters["filters"]


async def get_filters_names(user_id: int, chat_id: int) -> List[str]:
    _filters = []
    for _filter in await _get_filters(user_id, chat_id):
        _filters.append(_filter)
    return _filters


async def get_filter(user_id: int, chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _filters = await _get_filters(user_id, chat_id)
    if name in _filters:
        return _filters[name]
    return False


async def save_filter(user_id: int, chat_id: int, name: str, _filter: dict):
    name = name.lower().strip()
    _filters = await _get_filters(user_id, chat_id)
    _filters[name] = _filter
    await filtersdb.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"filters": _filters}},
        upsert=True,
    )


async def delete_filter(user_id: int, chat_id: int, name: str) -> bool:
    filtersd = await _get_filters(user_id, chat_id)
    name = name.lower().strip()
    if name in filtersd:
        del filtersd[name]
        await filtersdb.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {"$set": {"filters": filtersd}},
            upsert=True,
        )
        return True
    return False


async def blacklisted_chats(user_id: int) -> list:
    chats_list = []
    async for chat in blchatdb.users.find({"user_id": user_id, "chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list


async def blacklist_chat(user_id: int, chat_id: int) -> bool:
    if not await blchatdb.users.find_one({"user_id": user_id, "chat_id": chat_id}):
        await blchatdb.users.insert_one({"user_id": user_id, "chat_id": chat_id})
        return True
    return False


async def whitelist_chat(user_id: int, chat_id: int) -> bool:
    if await blchatdb.users.find_one({"user_id": user_id, "chat_id": chat_id}):
        await blchatdb.users.delete_one({"user_id": user_id, "chat_id": chat_id})
        return True
    return False


async def go_afk(user_id: int, time, reason=""):
    user_data = await afkdb.users.find_one({"user_id": user_id})
    if user_data:
        await afkdb.users.update_one(
            {"user_id": user_id},
            {"$set": {"afk": True, "time": time, "reason": reason}},
        )
    else:
        await afkdb.users.insert_one(
            {"user_id": user_id, "afk": True, "time": time, "reason": reason}
        )


async def no_afk(user_id: int):
    await afkdb.users.delete_one({"user_id": user_id, "afk": True})


async def check_afk(user_id: int):
    user_data = await afkdb.users.find_one({"user_id": user_id, "afk": True})
    return user_data


async def add_bots(user_id, api_id, api_hash, session_string):
    return await ubotdb.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "api_id": api_id,
                "api_hash": api_hash,
                "session_string": session_string,
            }
        },
        upsert=True,
    )


async def remove_bots(user_id):
    return await ubotdb.delete_one({"user_id": user_id})


async def get_userbots():
    data = []
    async for ubot in ubotdb.find({"user_id": {"$exists": 1}}):
        data.append(
            dict(
                name=str(ubot["user_id"]),
                api_id=ubot["api_id"],
                api_hash=ubot["api_hash"],
                session_string=ubot["session_string"],
            )
        )
    return data


async def get_prem():
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_prem(user_id):
    sudoers = await get_prem()
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_prem(user_id):
    sudoers = await get_prem()
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def get_seles():
    seles = await resell.find_one({"seles": "seles"})
    if not seles:
        return []
    return seles["reseller"]


async def add_seles(user_id):
    reseller = await get_seles()
    reseller.append(user_id)
    await resell.update_one(
        {"seles": "seles"}, {"$set": {"reseller": reseller}}, upsert=True
    )
    return True


async def remove_seles(user_id):
    reseller = await get_seles()
    reseller.remove(user_id)
    await resell.update_one(
        {"seles": "seles"}, {"$set": {"reseller": reseller}}, upsert=True
    )
    return True


async def get_expired_date(user_id):
    user = await expdb.users.find_one({"_id": user_id})
    if user:
        return user.get("expire_date")
    else:
        return None


async def set_expired_date(user_id, expire_date):
    await expdb.users.update_one(
        {"_id": user_id}, {"$set": {"expire_date": expire_date}}, upsert=True
    )


async def rem_expired_date(user_id):
    await expdb.users.update_one(
        {"_id": user_id}, {"$unset": {"expire_date": ""}}, upsert=True
    )
