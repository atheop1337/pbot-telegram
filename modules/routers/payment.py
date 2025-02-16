import logging
import os
import asyncio
from typing import Union

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiocryptopay import AioCryptoPay

from modules.libraries.dbms import Database
from modules.locales import en, ru

logger = logging.getLogger(__name__)

db = Database()

router = Router()

@router.message(Command("pay"))
async def create_invoice(message: types.Message, crypto: AioCryptoPay) -> None:
    """Creates an invoice and sends the payment link to the user."""
    invoice = await crypto.create_invoice(
        asset="TON", amount=0.1, payload=str(message.from_user.id)
    )
    await message.answer(f"Оплатите по ссылке: {invoice.bot_invoice_url}")


@router.message(Command("check_payment"))
async def check_payment(message: types.Message, crypto: AioCryptoPay) -> None:
    """
    Manually checks the payment status by searching for the user's invoice.
    Retrieves all invoices, filters by user ID, and checks the latest one.
    """
    user_id = str(message.from_user.id)
    try:
        invoices = await crypto.get_invoices()
    except Exception as e:
        logger.exception(f"Error retrieving invoices for user {user_id}: {e}")
        await message.answer("Ошибка при получении данных о платежах. Попробуйте позже.")
        return

    matching_invoices = [inv for inv in invoices if inv.payload == user_id]
    if not matching_invoices:
        await message.answer("Не найдено ни одного платежа для проверки.")
        return

    latest_invoice = max(matching_invoices, key=lambda inv: inv.created_at)
    if latest_invoice.status == "paid":
        await message.answer("Ваш платеж успешно принят!")
    else:
        await message.answer("Платеж еще не подтвержден. Попробуйте позже.")