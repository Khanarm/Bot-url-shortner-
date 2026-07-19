import asyncio
import requests

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN, API_URL


bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Shortener(StatesGroup):
    waiting_alias = State()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Welcome!\n\n"
        "Mujhe URL bhejo, phir main alias puchunga."
    )


@dp.message(lambda m: m.text.startswith(("http://", "https://")))
async def get_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)

    await message.answer(
        "✏️ Alias bhejo.\n\n"
        "Example:\n"
        "your brand name.\n\n"
        "Ya 'skip' likho."
    )

    await state.set_state(Shortener.waiting_alias)


@dp.message(Shortener.waiting_alias)
async def create_short(message: Message, state: FSMContext):

    data = await state.get_data()
    url = data["url"]

    alias = message.text.strip()

    if alias.lower() == "skip":
        alias = ""

    try:
        response = requests.post(
            API_URL,
            json={
                "url": url,
                "alias": alias
            }
        )

        data = response.json()

        if data.get("success"):
            await message.answer(
                f"✅ Short Link\n\n{data['short_url']}"
            )
        else:
            await message.answer("❌ Link create nahi hua.")

    except Exception:
        await message.answer("⚠️ Server error")

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
