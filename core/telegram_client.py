import os
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class TelegramNotifier:
    MAX_MESSAGE_LENGTH = 4000

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _split_message(self, text: str) -> list[str]:
        chunks = []
        while len(text) > self.MAX_MESSAGE_LENGTH:
            split_index = text.rfind('\n', 0, self.MAX_MESSAGE_LENGTH)

            if split_index == -1:
                split_index = self.MAX_MESSAGE_LENGTH

            chunks.append(text[:split_index])
            text = text[split_index:].lstrip()

        if text:
            chunks.append(text)

        return chunks

    async def send_report(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials missing. Skipping notification.")
            return

        chunks = self._split_message(text)

        async with aiohttp.ClientSession() as session:
            for index, chunk in enumerate(chunks):
                payload = {
                    "chat_id": self.chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown"
                }

                try:
                    async with session.post(self.api_url, json=payload) as response:
                        if response.status != 200:
                            error_msg = await response.text()
                            logger.error(f"Failed to send chunk {index + 1}/{len(chunks)}: {error_msg}")
                        else:
                            logger.info(f"Successfully sent chunk {index + 1}/{len(chunks)} to Telegram.")
                except Exception as e:
                    logger.error(f"Error sending Telegram message: {e}")

                if len(chunks) > 1:
                    await asyncio.sleep(1)