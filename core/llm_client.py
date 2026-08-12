import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class AsyncGeminiLLMClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

        self.response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING"},
                    "category": {
                        "type": "STRING",
                        "description": "automation, integration, analytics, support, consultation, or out_of_scope"
                    },
                    "target_department": {"type": "STRING"},
                    "priority": {
                        "type": "STRING",
                        "description": "low, medium, or high"
                    },
                    "short_summary": {"type": "STRING"},
                    "requested_actions": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "needs_clarification": {"type": "BOOLEAN"},
                    "missing_info_reason": {"type": "STRING"}
                },
                "required": [
                    "id", "category", "priority", "short_summary",
                    "requested_actions", "needs_clarification"
                ]
            }
        }

    async def process_batch_async(self, batch: list, retries: int = 3) -> list:
        prompt = self._build_prompt(batch)

        for attempt in range(retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=self.response_schema,
                        temperature=0.0,
                    ),
                )

                parsed_data = json.loads(response.text)
                return parsed_data

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Executing repair/retry...")

        logger.error("Failed to process batch after all attempts.")
        return []

    def _build_prompt(self, batch: list) -> str:
        return f"Analyze these requests and map them strictly to the schema:\n{json.dumps(batch, ensure_ascii=False)}"