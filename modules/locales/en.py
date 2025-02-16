from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Messages:

    @staticmethod
    def welcome():
        return "You're already registered, use /profile to start using bot"

    @staticmethod
    def profile(user_data: dict) -> str:
        return (
            f"👤 <b>Name:</b> {user_data['username'] or 'Not specified'}\n"
            f"🆔 <b>ID:</b> {user_data['user_id']}\n"
            f"📅 <b>Registration date:</b> {user_data['registration_date']}\n"
            f"💰 <b>Balance:</b> {user_data['balance']}$\n"
            f"⚡ <b>Administrator:</b> {'Yes' if user_data['is_admin'] else 'No'}"
        )


class KeyBoards:

    @staticmethod
    def language_buttons():
        kb = [
            [InlineKeyboardButton(text="🇷🇺 Russian", callback_data="ru")],
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="en")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)