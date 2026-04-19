from abc import abstractmethod
from typing import Dict, List
import numpy as np

from ..core.interfaces import IModel, Parameter, PlotConfig


class BaseModel(IModel):
    """Базовый класс — общая реализация для всех моделей."""

    _name: str = "Базовая модель"
    _description: str = ""
    _parameters: List[Parameter] = []
    _state_names: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters.copy()

    @property
    def state_names(self) -> List[str]:
        return self._state_names.copy()

    def get_default_parameters(self) -> Dict[str, float]:
        return {p.name: p.default_value for p in self._parameters}

    @abstractmethod
    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        pass

    @abstractmethod
    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        pass

    @abstractmethod
    def get_plot_config(self) -> PlotConfig:
        pass