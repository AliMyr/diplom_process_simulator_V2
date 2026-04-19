import json
from pathlib import Path
import numpy as np

from ..core.interfaces import SimulationResult


class CSVExporter:

    @property
    def file_extension(self) -> str:
        return ".csv"

    @property
    def description(self) -> str:
        return "CSV таблица"

    def export(self, result: SimulationResult, filepath: str) -> bool:
        try:
            path = Path(filepath)
            headers = ["time"] + list(result.states.keys())

            with open(path, 'w', encoding='utf-8') as f:
                f.write(",".join(headers) + "\n")
                for i in range(len(result.time)):
                    row = [str(result.time[i])]
                    for values in result.states.values():
                        row.append(str(values[i]))
                    f.write(",".join(row) + "\n")

            return True
        except Exception as e:
            print(f"Ошибка экспорта CSV: {e}")
            return False


class JSONExporter:

    @property
    def file_extension(self) -> str:
        return ".json"

    @property
    def description(self) -> str:
        return "JSON файл"

    def export(self, result: SimulationResult, filepath: str) -> bool:
        try:
            data = {
                "time": result.time.tolist(),
                "states": {k: v.tolist() for k, v in result.states.items()},
                "metadata": result.metadata
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка экспорта JSON: {e}")
            return False


class ExporterFactory:

    _exporters = {
        'csv': CSVExporter,
        'json': JSONExporter,
    }

    @classmethod
    def create(cls, format_type: str):
        if format_type not in cls._exporters:
            raise ValueError(f"Неизвестный формат: {format_type}")
        return cls._exporters[format_type]()

    @classmethod
    def get_format_descriptions(cls) -> dict:
        return {name: cls._exporters[name]().description for name in cls._exporters}