import os
import asyncio
import logging
import platform
from pathlib import Path
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.models.update import Update

from modules.libraries.dbms import Database
from modules.libraries.utils import read_tokens
from modules.routers.routers import router as handlers_router

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configures logging to file and console."""
    log_format = "[%(asctime)s]:%(levelname)s:%(funcName)s:%(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d|%H:%M:%S",
        handlers=[
            logging.FileHandler(Path(".logs") / "logs.log"),
            logging.StreamHandler(),
        ],
    )


async def init_crypto(crypto_token: str) -> AioCryptoPay:
    """Initializes AioCryptoPay and registers payment handler."""
    crypto = AioCryptoPay(token=crypto_token, network=Networks.TEST_NET)

    @crypto.pay_handler()
    async def invoice_paid(update: Update, app) -> None:
        """Handles invoice payment updates."""
        logger.info(f"Invoice paid update: {update}")
        invoice = update.payload
        user_id = invoice.payload
        if user_id:
            try:
                await app["bot"].send_message(user_id, "Ваш платеж успешно принят! Спасибо!")
                logger.info(f"Notification sent to user {user_id}")
            except Exception as e:
                logger.exception(f"Error sending payment notification to user {user_id}: {e}")
        else:
            logger.warning(f"No user id found in invoice payload: {invoice}")

    return crypto


async def init_web_server(crypto: AioCryptoPay, bot: Bot) -> None:
    """Creates and starts a web server for handling updates from the crypto service."""
    app = web.Application()
    app["bot"] = bot
    app["crypto"] = crypto
    app.add_routes([web.post("/crypto-secret-path", crypto.get_updates)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="localhost", port=3001)
    await site.start()
    logger.info("Web server started at http://localhost:3001")


async def main() -> None:
    """Main bot entry point."""
    tokens = read_tokens()
    telegram_token = tokens.get("telegram")
    crypto_token = tokens.get("crypto")
    if not telegram_token or not crypto_token:
        raise ValueError("Missing required tokens: telegram and/or crypto")

    crypto = await init_crypto(crypto_token)
    bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Database()
    dp = Dispatcher()
    dp.include_router(handlers_router)
    dp["crypto"] = crypto

    logger.info(f"Bot starting on {platform.system()} {platform.release()}")

    try:
        await db.create_tables()
        await asyncio.gather(
            init_web_server(crypto, bot),
            dp.start_polling(bot),
        )
    except Exception as ex:
        logger.exception(f"Unhandled error occurred: {ex}")
    finally:
        await bot.session.close()
        await crypto.close()


if __name__ == "__main__":
    for directory in [".logs", ".database", ".pics"]:
        os.makedirs(directory, exist_ok=True)

    setup_logging()

    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)