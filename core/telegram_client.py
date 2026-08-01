import os
import aiohttp
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_report(self, report_text: str) -> None:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials missing in .env. Skipping notification.")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": report_text,
            "parse_mode": "HTML"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Report successfully sent to Telegram.")
                    else:
                        error_msg = await response.text()
                        logger.error(f"Failed to send Telegram message: {error_msg}")
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")