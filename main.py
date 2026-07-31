import os
import asyncio
from dotenv import load_dotenv
from core.io_handlers import CSVDataReader, LocalDataWriter
from core.llm_client import AsyncGeminiLLMClient

def _ensure_input_file(filepath: str) -> None:
    if not os.path.exists(filepath):
        with open(filepath, mode='w', encoding='utf-8') as file_obj:
            file_obj.write("id,channel,timestamp,raw_text\n")
            file_obj.write("1,slack,2023-10-01T10:00:00Z,Зробіть інтеграцію з CRM для сейлзів, дуже треба на вчора\n")

def _create_batches(data: list, batch_size: int) -> list:
    return [data[i:i + batch_size] for i in range(0, len(data), batch_size)]

async def run_pipeline():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    input_file = "input_requests.csv"
    _ensure_input_file(input_file)

    reader = CSVDataReader()
    writer = LocalDataWriter()
    llm_client = AsyncGeminiLLMClient(api_key=api_key)

    requests = reader.read(input_file)
    batches = _create_batches(requests, 50)
    semaphore = asyncio.Semaphore(1)

    async def process_with_limit(batch):
        async with semaphore:
            return await llm_client.process_batch_async(batch)

    tasks = [process_with_limit(batch) for batch in batches]
    batch_results = await asyncio.gather(*tasks)

    parsed_requests = [req for batch in batch_results for req in batch]

    writer.write_json(parsed_requests, "output.json")
    writer.write_report(parsed_requests, "report.md")

if __name__ == "__main__":
    asyncio.run(run_pipeline())