import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SimulationPreset:
    name: str
    model_name: str
    parameters: Dict[str, float]
    simulation_settings: Dict[str, Any]  # t_start, t_end, num_points
    created_at: str = ""
    description: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class PresetManager:
    def __init__(self, presets_dir: Optional[Path] = None):
        if presets_dir is None:
            presets_dir = Path.home() / ".diplom_simulator" / "presets"

        self.presets_dir = presets_dir
        self.presets_dir.mkdir(parents=True, exist_ok=True)

    def save_preset(self, preset: SimulationPreset) -> bool:
        try:
            filepath = self.presets_dir / f"{preset.name}.json"
            data = asdict(preset)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения preset: {e}")
            return False

    def load_preset(self, name: str) -> Optional[SimulationPreset]:
        try:
            filepath = self.presets_dir / f"{name}.json"
            if not filepath.exists():
                print(f"Preset '{name}' не найден")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SimulationPreset(**data)
        except Exception as e:
            print(f"Ошибка загрузки preset: {e}")
            return None

    def list_presets(self) -> List[str]:
        return [f.stem for f in self.presets_dir.glob("*.json")]

    def delete_preset(self, name: str) -> bool:
        try:
            filepath = self.presets_dir / f"{name}.json"
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления preset: {e}")
            return False

    def get_preset_info(self, name: str) -> Optional[Dict[str, Any]]:
        preset = self.load_preset(name)
        if preset:
            return {
                "name": preset.name,
                "model": preset.model_name,
                "created": preset.created_at,
                "description": preset.description,
            }
        return None