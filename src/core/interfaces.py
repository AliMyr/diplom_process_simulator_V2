from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Callable
from enum import Enum, auto
import numpy as np

# Состояния симуляции
class SimulationState(Enum):
    IDLE = auto()
    RUNNING = auto()
    COMPLETED = auto()
    ERROR = auto()

# Данные
@dataclass
class Parameter:
    name: str           # внутреннее имя, например 'mass'
    display_name: str   # отображаемое, например 'Масса'
    default_value: float
    min_value: float
    max_value: float
    step: float = 0.1
    unit: str = ""
    description: str = ""


@dataclass
class SimulationResult:
    time: np.ndarray
    states: Dict[str, np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlotConfig:
    title: str
    xlabel: str
    ylabel: str
    legend_labels: List[str]
    colors: List[str] = field(default_factory=list)
    grid: bool = True

# Интерфейсы. Каждая модель должна реализовать эти методы
class IModel(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[Parameter]:
        pass

    @property
    @abstractmethod
    def state_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        pass

    @abstractmethod
    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        pass

    @abstractmethod
    def get_plot_config(self) -> PlotConfig:
        pass

# Интерфейс решателя дифференциальных уравнений
class ISolver(ABC):

    @abstractmethod
    def solve(
        self,
        derivatives: Callable[[float, np.ndarray], np.ndarray],
        initial_state: np.ndarray,
        t_span: Tuple[float, float],
        t_eval: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        pass

# Интерфейс движка симуляции
class ISimulationEngine(ABC):

    @abstractmethod
    def set_model(self, model: IModel) -> None:
        pass

    @abstractmethod
    def set_parameters(self, params: Dict[str, float]) -> None:
        pass

    @abstractmethod
    def run(self, t_start: float, t_end: float, num_points: int) -> SimulationResult:
        pass

    @abstractmethod
    def get_state(self) -> SimulationState:
        pass