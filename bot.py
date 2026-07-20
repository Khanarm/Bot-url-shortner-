import asyncio
import re
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN, API_URL, MAX_LINKS


bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Shortener(StatesGroup):
    waiting_alias = State()


URL_REGEX = re.compile(
    r"https?://[^\s]+",
    re.IGNORECASE
)


async def shorten_url(session, url, alias):
    try:
        async with session.post(
            API_URL,
            json={
                "url": url,
                "alias": alias
            }
        ) as response:

            data = await response.json()

            if data.get("success"):
                return url, data["short_url"]

            return url, url

    except Exception:
        return url, url


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Welcome!\n\n"
        "📌 Ek message me maximum 40 links bhejo.\n"
        "✏️ Main sirf ek baar alias puchunga.\n"
        "🚀 Fir sab links short karke same message wapas bhej dunga."
)

@dp.message()
async def receive_message(message: Message, state: FSMContext):

    if not message.text:
        return

    original_text = message.text

    urls = URL_REGEX.findall(original_text)

    if len(urls) == 0:
        await message.answer(
            "❌ Is message me koi link nahi mila."
        )
        return

    if len(urls) > MAX_LINKS:
        await message.answer(
            f"❌ Ek message me maximum {MAX_LINKS} links hi short kiye ja sakte hain."
        )
        return

    await state.update_data(
        original_text=original_text,
        urls=urls
    )

    await message.answer(
        f"🔗 Total Links: {len(urls)}\n\n"
        "✏️ Ab alias bhejo.\n\n"
        "Example:\n"
        "ckdrama"
    )

    await state.set_state(Shortener.waiting_alias)

@dp.message(Shortener.waiting_alias)
async def receive_alias(message: Message, state: FSMContext):
    alias = message.text.strip()

    if " " in alias:
        await message.answer("❌ Alias me space allowed nahi hai.")
        return

    data = await state.get_data()

    original_text = data["original_text"]
    urls = data["urls"]

    new_text = original_text

    for i, url in enumerate(urls):
        current_alias = alias if i == 0 else f"{alias}{i+1}"

        try:
            response = requests.post(
                f"{API_BASE}/api/shorten",
                json={
                    "url": url,
                    "alias": current_alias
                },
                timeout=20
            )

            if response.status_code != 200:
                await message.answer(
                    f"❌ Link short nahi hua.\nAlias: {current_alias}"
                )
                await state.clear()
                return

            result = response.json()

            short_url = result.get("short_url")

            if not short_url:
                await message.answer("❌ API error.")
                await state.clear()
                return

            new_text = new_text.replace(url, short_url, 1)

        except Exception as e:
            await message.answer(f"❌ Error:\n{e}")
            await state.clear()
            return

    await message.answer(
        "✅ Sabhi links successfully short ho gaye:\n\n"
        f"{new_text}"
    )

    await state.clear()

