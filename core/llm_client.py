import json
import asyncio
import re
import logging
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from pydantic import ValidationError
from typing import List, Dict
from core.models import RawRequest, ParsedRequest, Category, Priority
from core.interfaces import LLMClient

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class AsyncGeminiLLMClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gemini-3.1-flash-lite"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    async def process_batch_async(self, requests: List[RawRequest]) -> List[ParsedRequest]:
        if not requests:
            return []

        prompt = self._build_batch_prompt(self._prepare_input(requests))

        for _ in range(2):
            try:
                response = await self.model.generate_content_async(prompt)
                raw_json = self._extract_json_string(response.text)
                data_list = json.loads(raw_json)
                parsed_dict = self._validate_items(data_list)

                if parsed_dict:
                    return self._map_results(requests, parsed_dict)

            except GoogleAPIError as e:
                logger.error(f"Google API Error: {e}")
                await asyncio.sleep(5)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Parsing Error: {e}")
                await asyncio.sleep(2)

        return [self._get_fallback(req.id, "Batch processing completely failed.") for req in requests]

    def _prepare_input(self, requests: List[RawRequest]) -> str:
        input_data = [{"id": req.id, "text": req.raw_text} for req in requests]
        return json.dumps(input_data, ensure_ascii=False)

    def _extract_json_string(self, text: str) -> str:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return match.group(0) if match else text

    def _validate_items(self, data_list: List[dict]) -> Dict[str, ParsedRequest]:
        parsed_dict = {}
        for data in data_list:
            try:
                if isinstance(data.get("category"), str):
                    data["category"] = data["category"].lower()
                if isinstance(data.get("priority"), str):
                    data["priority"] = data["priority"].lower()

                parsed = ParsedRequest(**data)
                parsed_dict[parsed.id] = parsed
            except ValidationError as ve:
                logger.error(f"Validation error for ID {data.get('id')}: {ve}")
        return parsed_dict

    def _map_results(self, requests: List[RawRequest], parsed_dict: Dict[str, ParsedRequest]) -> List[ParsedRequest]:
        results = []
        for req in requests:
            if req.id in parsed_dict:
                results.append(parsed_dict[req.id])
            else:
                results.append(self._get_fallback(req.id, "Item missing or validation failed."))
        return results

    def _get_fallback(self, req_id: str, reason: str) -> ParsedRequest:
        return ParsedRequest(
            id=req_id,
            category=Category.OUT_OF_SCOPE,
            priority=Priority.LOW,
            short_summary="Processing failed.",
            needs_clarification=True,
            missing_info_reason=reason
        )

    def _build_batch_prompt(self, json_input: str) -> str:
        return f"""
        Analyze the following JSON array of incoming requests.
        For EACH request, extract the information and return a JSON array of objects.
        The output MUST be a valid JSON array strictly matching this schema for each object:
        [
            {{
                "id": "must exactly match the id from the input",
                "category": "автоматизація" | "інтеграція" | "звіт/аналітика" | "баг/підтримка" | "питання/консультація" | "поза скоупом",
                "target_department": "string or null",
                "priority": "low" | "medium" | "high",
                "short_summary": "string",
                "requested_actions": ["string", "string"],
                "needs_clarification": boolean,
                "missing_info_reason": "string or null"
            }}
        ]

        IMPORTANT:
        - 'category' and 'priority' MUST be strictly lowercase and match the allowed options EXACTLY.
        - Return ONLY the JSON array, no extra text, no markdown blocks.

        Input requests:
        {json_input}
        """