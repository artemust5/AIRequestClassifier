import json
import asyncio
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from pydantic import ValidationError
from core.models import RawRequest, ParsedRequest, Category, Priority
from core.interfaces import LLMClient


class AsyncGeminiLLMClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    async def process_request_async(self, request: RawRequest) -> ParsedRequest:
        prompt = self._build_prompt(request.raw_text)

        for attempt in range(3):
            try:
                response = await self.model.generate_content_async(prompt)
                data = json.loads(response.text)
                data["id"] = request.id
                return ParsedRequest(**data)
            except (json.JSONDecodeError, ValidationError, GoogleAPIError):
                await asyncio.sleep(2 ** attempt)
                continue

        return ParsedRequest(
            id=request.id,
            category=Category.OUT_OF_SCOPE,
            priority=Priority.LOW,
            short_summary="Processing failed.",
            needs_clarification=True,
            missing_info_reason="LLM validation or API call failed after retries."
        )

    def _build_prompt(self, text: str) -> str:
        return f"""
        Analyze the following text and extract the information in JSON format strictly matching this schema:
        {{
            "category": "автоматизація" | "інтеграція" | "звіт/аналітика" | "баг/підтримка" | "питання/консультація" | "поза скоупом",
            "target_department": "string or null",
            "priority": "low" | "medium" | "high",
            "short_summary": "string",
            "requested_actions": ["string", "string"],
            "needs_clarification": boolean,
            "missing_info_reason": "string or null"
        }}

        Text to analyze: {text}
        """