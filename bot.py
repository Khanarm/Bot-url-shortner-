import asyncio
import requests

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN, API_URL


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Welcome!\n\n"
        "Mujhe koi bhi URL bhejo, main uska short link bana dunga."
    )


@dp.message()
async def shorten(message: Message):

    url = message.text

    if not url.startswith(("http://", "https://")):
        await message.answer(
            "❌ Please valid URL bhejo."
        )
        return


    try:
        response = requests.post(
            API_URL,
            json={
                "url": url
            }
        )

        data = response.json()


        if data.get("success"):

            await message.answer(
                "✅ Short Link Created\n\n"
                f"🔗 {data['short_url']}"
            )

        else:
            await message.answer(
                "❌ Link create nahi hua."
            )

    except Exception as e:

        await message.answer(
            "⚠️ Server error"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
