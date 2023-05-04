import imaplib
import email
from email.header import decode_header
import traceback
import base64
import re
from datetime import datetime
import config
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import asyncio
import csv

def get_list_from_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

async def send_message(message, rpl=None, prv=None):
    bot = Bot(token=config.bot_key)
    #await bot.get_session()
    obj = await bot.send_message(
        chat_id=config.chat_id,
        text=message,
        parse_mode="HTML",
        reply_to_message_id=rpl,
        disable_web_page_preview=prv,
    )
    await asyncio.sleep(3)
    await bot._session.close()
    return obj.message_id

def post_construct(headline, text, lenth, link):
    width=""
    for i in range(lenth):
        width+="\U0001F525"
    txt = ""
    txt += (
        width
        +"\n<b>"
        + str(headline)
        + "</b>"
        + "\n\n"
        + str(text)
        + "\n\n"
        + link      
    )
    return txt