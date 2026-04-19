# tests/test_presets.py

import pytest
import tempfile
from pathlib import Path
from src.utils.presets import PresetManager, SimulationPreset


@pytest.fixture
def temp_presets_dir():
    """Временная директория для тестирования preset-ов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestPresetManager:
    def test_save_and_load_preset(self, temp_presets_dir):
        manager = PresetManager(temp_presets_dir)

        preset = SimulationPreset(
            name="test_preset",
            model_name="Гармонический осциллятор",
            parameters={"m": 1.0, "k": 10.0, "gamma": 0.5, "x0": 1.0, "v0": 0.0},
            simulation_settings={"t_start": 0, "t_end": 10, "num_points": 1000},
            description="Test preset"
        )

        assert manager.save_preset(preset)

        loaded = manager.load_preset("test_preset")
        assert loaded is not None
        assert loaded.name == "test_preset"
        assert loaded.parameters["m"] == 1.0

    def test_list_presets(self, temp_presets_dir):
        manager = PresetManager(temp_presets_dir)

        preset1 = SimulationPreset(
            name="preset1",
            model_name="Model1",
            parameters={},
            simulation_settings={}
        )
        preset2 = SimulationPreset(
            name="preset2",
            model_name="Model2",
            parameters={},
            simulation_settings={}
        )

        manager.save_preset(preset1)
        manager.save_preset(preset2)

        presets = manager.list_presets()
        assert len(presets) == 2
        assert "preset1" in presets
        assert "preset2" in presets

    def test_delete_preset(self, temp_presets_dir):
        manager = PresetManager(temp_presets_dir)

        preset = SimulationPreset(
            name="to_delete",
            model_name="Model",
            parameters={},
            simulation_settings={}
        )

        manager.save_preset(preset)
        assert manager.delete_preset("to_delete")
        assert "to_delete" not in manager.list_presets()