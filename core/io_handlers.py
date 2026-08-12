import csv
import json
import logging
from typing import List, Dict, Any
from collections import Counter
from core.interfaces import DataReader, DataWriter

logger = logging.getLogger(__name__)


class CSVDataReader(DataReader):
    def read(self, filepath: str) -> List[Dict[str, Any]]:
        required_columns = {'id', 'raw_text'}
        requests = []

        with open(filepath, mode='r', encoding='utf-8-sig') as file_obj:
            reader = csv.DictReader(file_obj)

            if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns in CSV. Expected: {required_columns}")

            for row in reader:
                requests.append(row)

        return requests


class JSONDataWriter(DataWriter):
    def write(self, data: List[Dict[str, Any]], filepath: str) -> None:
        with open(filepath, mode='w', encoding='utf-8') as file_obj:
            json.dump(data, file_obj, ensure_ascii=False, indent=4)
        logger.info(f"JSON data successfully saved to {filepath}")


class MarkdownReportWriter(DataWriter):
    def write(self, data: List[Dict[str, Any]], filepath: str) -> None:
        category_counts = Counter(req.get('category', 'unknown') for req in data)
        priority_counts = Counter(req.get('priority', 'unknown') for req in data)
        dept_counts = Counter(req.get('target_department') for req in data if req.get('target_department'))
        clarification_needed = [req for req in data if req.get('needs_clarification')]

        with open(filepath, mode='w', encoding='utf-8') as file_obj:
            file_obj.write("# Звіт класифікації запитів\n\n")

            file_obj.write("## Розподіл за категоріями\n")
            for category_name, count in category_counts.items():
                file_obj.write(f"- {category_name}: {count}\n")

            file_obj.write("\n## Розподіл за пріоритетом\n")
            for priority_name, count in priority_counts.items():
                file_obj.write(f"- {priority_name}: {count}\n")

            file_obj.write("\n## Розподіл за відділами\n")
            for dept_name, count in dept_counts.items():
                file_obj.write(f"- {dept_name}: {count}\n")

            file_obj.write("\n## Запити, що потребують уточнення\n")
            for req in clarification_needed:
                reason = req.get('missing_info_reason') or 'Не вказано'
                file_obj.write(f"- ID: {req.get('id', 'N/A')} | Причина: {reason}\n")

        logger.info(f"Markdown report successfully saved to {filepath}")