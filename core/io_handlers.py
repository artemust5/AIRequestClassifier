import csv
import json
from typing import List
from collections import Counter
from core.models import RawRequest, ParsedRequest
from core.interfaces import DataReader, DataWriter


class CSVDataReader(DataReader):
    def read(self, filepath: str) -> List[RawRequest]:
        requests = []
        with open(filepath, mode='r', encoding='utf-8-sig') as file_obj:
            reader = csv.DictReader(file_obj)
            for row in reader:
                requests.append(RawRequest(**row))
        return requests


class LocalDataWriter(DataWriter):
    def write_json(self, data: List[ParsedRequest], filepath: str) -> None:
        with open(filepath, mode='w', encoding='utf-8') as file_obj:
            json_data = [item.model_dump(mode='json') for item in data]
            json.dump(json_data, file_obj, ensure_ascii=False, indent=4)

    def write_report(self, data: List[ParsedRequest], filepath: str) -> None:
        category_counts = Counter(req.category.value for req in data)
        priority_counts = Counter(req.priority.value for req in data)
        dept_counts = Counter(req.target_department for req in data if req.target_department)
        clarification_needed = [req for req in data if req.needs_clarification]

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
                reason = req.missing_info_reason or 'Не вказано'
                file_obj.write(f"- ID: {req.id} | Причина: {reason}\n")