from typing import Dict, Optional
from functools import partial
import numpy as np

from .interfaces import IModel, ISolver, ISimulationEngine, SimulationState, SimulationResult
from .solver import SolverFactory


class SimulationEngine(ISimulationEngine):
    """Движок — связывает модель и решатель, запускает симуляцию."""

    def __init__(self, solver: Optional[ISolver] = None):
        self._solver = solver or SolverFactory.create('scipy')
        self._model: Optional[IModel] = None
        self._parameters: Dict[str, float] = {}
        self._state = SimulationState.IDLE
        self._last_result: Optional[SimulationResult] = None

    def set_model(self, model: IModel) -> None:
        self._model = model
        self._parameters = {p.name: p.default_value for p in model.parameters}
        self._state = SimulationState.IDLE

    def set_parameters(self, params: Dict[str, float]) -> None:
        if self._model is None:
            raise RuntimeError("Модель не установлена")
        self._parameters.update(params)

    def get_state(self) -> SimulationState:
        return self._state

    @property
    def last_result(self) -> Optional[SimulationResult]:
        return self._last_result

    def run(self, t_start: float, t_end: float, num_points: int) -> SimulationResult:
        if self._model is None:
            raise RuntimeError("Модель не установлена")
        if t_end <= t_start:
            raise ValueError("Конечное время должно быть больше начального")

        self._state = SimulationState.RUNNING

        try:
            initial_state = self._model.get_initial_state(self._parameters)

            derivatives_func = partial(
                self._model.derivatives,
                params=self._parameters
            )

            t_eval = np.linspace(t_start, t_end, num_points)

            time, states = self._solver.solve(
                derivatives_func,
                initial_state,
                (t_start, t_end),
                t_eval
            )

            states_dict = {
                name: states[i, :]
                for i, name in enumerate(self._model.state_names)
            }

            result = SimulationResult(
                time=time,
                states=states_dict,
                metadata={
                    'model': self._model.name,
                    'parameters': self._parameters.copy(),
                    't_start': t_start,
                    't_end': t_end,
                    'num_points': num_points
                }
            )

            self._last_result = result
            self._state = SimulationState.COMPLETED
            return result

        except Exception as e:
            self._state = SimulationState.ERROR
            raise RuntimeError(f"Ошибка симуляции: {e}") from e