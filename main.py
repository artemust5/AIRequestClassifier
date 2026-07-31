import os
import asyncio
from dotenv import load_dotenv
from core.io_handlers import CSVDataReader, LocalDataWriter
from core.llm_client import AsyncGeminiLLMClient


async def run_pipeline():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    reader = CSVDataReader()
    writer = LocalDataWriter()
    llm_client = AsyncGeminiLLMClient(api_key=api_key)

    input_file = "input_requests.csv"

    if not os.path.exists(input_file):
        with open(input_file, mode='w', encoding='utf-8') as file_obj:
            file_obj.write("id,channel,timestamp,raw_text\n")
            file_obj.write("1,slack,2023-10-01T10:00:00Z,Зробіть інтеграцію з CRM для сейлзів, дуже треба на вчора\n")
            file_obj.write("2,email,2023-10-01T10:05:00Z,Не працює кнопка логіну на сайті.\n")
            file_obj.write("3,telegram,2023-10-01T10:10:00Z,Як згенерувати звіт за місяць?\n")

    requests = reader.read(input_file)

    semaphore = asyncio.Semaphore(2)

    async def process_with_limit(req):
        async with semaphore:
            return await llm_client.process_request_async(req)

    tasks = [process_with_limit(req) for req in requests]
    parsed_requests = await asyncio.gather(*tasks)

    writer.write_json(parsed_requests, "output.json")
    writer.write_report(parsed_requests, "report.md")


def main():
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()