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
            json={
    "urls": urls,
    "suffix": "ckdrama"
}
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

@dp.message(F.text)
async def process_message(message: Message):

    processing = await message.reply(
        "⏳ Processing links..."
    )

    try:

        result = await replace_links(message.text)

        if result is None:
            await processing.edit_text(
                "❌ No links found."
            )
            return

        # Telegram message limit
        if len(result) <= 4096:

            await processing.edit_text(result)

        else:

            # Agar message bahut bada ho
            for i in range(0, len(result), 4096):
                await message.answer(
                    result[i:i + 4096]
                )

            await processing.delete()

    except Exception as e:

        await processing.edit_text(
            f"❌ Error:\n{e}"
        )


async def main():

    print("✅ URL Shortener Bot Started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
