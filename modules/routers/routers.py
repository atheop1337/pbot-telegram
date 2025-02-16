import logging
import os
import asyncio
from typing import Union

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart

from modules.libraries.dbms import Database
from modules.locales import en, ru

logger = logging.getLogger(__name__)

db = Database()
router = Router()


@router.message(CommandStart())
async def command_start(message: types.Message) -> None:
    """Command /start handler."""
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info(f"Handling /start for user_id={user_id}, username={username}")

    user_data = await db.fetch_info(user_id)

    if user_data is False:
        logger.error(f"Database error while fetching info for user_id={user_id}")
        await message.answer("Something went wrong. Try again later.")
        return

    if user_data is None:
        logger.info(f"New user detected: user_id={user_id}, username={username}")
        await message.answer(
            f"Hello, {username}! Before we start, please select a language. You can edit this later.",
            reply_markup=en.KeyBoards.language_buttons()
        )
    else:
        language = user_data["language"]
        reply = {
            "en": en.Messages.welcome(),
            "ru": ru.Messages.welcome(),
        }.get(language)
        logger.info(f"Existing user: user_id={user_id}, language={language}")
        await message.answer(str(reply))


@router.message(Command("profile"))
async def command_profile(message: types.Message) -> None:
    user_id = message.from_user.id
    logger.info(f"Handling /profile for user_id={user_id}")

    user_data = await db.fetch_info(user_id)

    if user_data is False:
        logger.error(f"Database error while fetching profile for user_id={user_id}")
        await message.answer("Something went wrong. Try again later.")
        return

    if user_data is None:
        logger.warning(f"Profile requested but no data found for user_id={user_id}")
        return

    language = user_data["language"]
    reply = {
        "en": en.Messages.profile(user_data),
        "ru": ru.Messages.profile(user_data)
    }.get(language)
    logger.info(f"Sending profile data for user_id={user_id}, language={language}")
    await message.answer(str(reply))


@router.callback_query(F.data == "profile")
async def callback_profile(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    logger.info(f"Handling profile callback for user_id={user_id}")

    user_data = await db.fetch_info(user_id)

    if user_data is False:
        logger.error(f"Database error while fetching profile for user_id={user_id}")
        await callback_query.answer("Something went wrong. Try again later.", show_alert=True)
        return

    if user_data is None:
        logger.warning(f"Profile callback but no data found for user_id={user_id}")
        return

    language = user_data["language"]
    reply = {
        "en": en.Messages.profile(user_data),
        "ru": ru.Messages.profile(user_data)
    }.get(language)
    logger.info(f"Updating profile message for user_id={user_id}, language={language}")
    await callback_query.message.edit_text(str(reply))


@router.callback_query(F.data.in_({"en", "ru"}))
async def select_language(callback_query: types.CallbackQuery) -> None:
    """Change language handler."""
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    language = callback_query.data
    logger.info(f"Language selection: user_id={user_id}, username={username}, new_language={language}")

    user_data = await db.fetch_info(user_id)

    if user_data is False:
        logger.error(f"Database error while fetching info for user_id={user_id}")
        await callback_query.answer("Something went wrong. Try again later.", show_alert=True)
        return

    if user_data is None:
        logger.info(f"Creating new user with language {language}: user_id={user_id}, username={username}")
        await db.create_user(user_id, username, language)
        await callback_query.answer("Profile created successfully.")
    else:
        logger.info(f"Updating language for user_id={user_id} to {language}")
        await db.update_user(user_id, "language", language)
        await callback_query.answer("Language updated successfully.")

    await callback_profile(callback_query)
