# tests/test_export.py

import pytest
import tempfile
from pathlib import Path
import json
import csv
from src.utils.export import CSVExporter, JSONExporter
from src.core.interfaces import SimulationResult
import numpy as np


@pytest.fixture
def sample_result():
    """Создать тестовый результат симуляции."""
    return SimulationResult(
        time=np.linspace(0, 10, 100),
        states={
            "x": np.sin(np.linspace(0, 10, 100)),
            "v": np.cos(np.linspace(0, 10, 100))
        },
        metadata={"model": "Test", "parameters": {"k": 1.0}}
    )


class TestCSVExporter:
    def test_export_csv(self, sample_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.csv"
            exporter = CSVExporter()

            assert exporter.export(sample_result, str(filepath))
            assert filepath.exists()

            # Проверить содержимое
            with open(filepath) as f:
                reader = csv.reader(f)
                header = next(reader)
                assert header == ["time", "x", "v"]
                rows = list(reader)
                assert len(rows) == 100


class TestJSONExporter:
    def test_export_json(self, sample_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            exporter = JSONExporter()

            assert exporter.export(sample_result, str(filepath))
            assert filepath.exists()

            # Проверить содержимое
            with open(filepath) as f:
                data = json.load(f)
                assert "time" in data
                assert "states" in data
                assert len(data["time"]) == 100