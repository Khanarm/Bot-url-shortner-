import re
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, API_URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


URL_REGEX = re.compile(
    r"https?://[^\s]+"
)


async def shorten_url(session, url):
    try:
        async with session.post(
            API_URL,
            json={"url": url},
            timeout=20
        ) as resp:

            if resp.status != 200:
                return url

            data = await resp.json()

            if data.get("success"):
                return data["short_url"]

            return url

    except Exception:
        return url


async def replace_links(text: str):

    links = URL_REGEX.findall(text)

    if not links:
        return None

    # Duplicate links remove
    unique_links = list(dict.fromkeys(links))

    async with aiohttp.ClientSession() as session:

        tasks = [
            shorten_url(session, link)
            for link in unique_links
        ]

        results = await asyncio.gather(*tasks)

    mapping = dict(zip(unique_links, results))

    new_text = text

    for old, new in mapping.items():
        new_text = new_text.replace(old, new)

    return new_text


@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 Welcome!\n\n"
        "📩 Mujhe koi bhi message bhejo.\n"
        "🔗 Message me jitne links honge sab short kar dunga.\n"
        "📝 Text aur emoji bilkul same rahenge."
    )
