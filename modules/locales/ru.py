from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Messages:

    @staticmethod
    def welcome() -> str:
        return "Вы уже зарегистрированы, используйте /profile, чтобы начать использовать бота"

    @staticmethod
    def profile(user_data: dict) -> str:
        return (
            f"👤 <b>Имя:</b> {user_data['username'] or 'Не указано'}\n"
            f"🆔 <b>ID:</b> {user_data['user_id']}\n"
            f"📅 <b>Дата регистрации:</b> {user_data['registration_date']}\n"
            f"💰 <b>Баланс:</b> {user_data['balance']}$\n"
            f"⚡ <b>Администратор:</b> {'Да' if user_data['is_admin'] else 'Нет'}"
        )


class KeyBoards:

    @staticmethod
    def welcome_buttons():
        kb = [
            [InlineKeyboardButton(text="🇷🇺 Russian", callback_data="ru")],
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="en")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)