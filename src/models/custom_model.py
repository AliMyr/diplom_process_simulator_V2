import numpy as np
from typing import Dict, List

from ..core.interfaces import IModel, Parameter, PlotConfig


_SAFE_MATH = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'exp': np.exp, 'log': np.log, 'log10': np.log10,
    'sqrt': np.sqrt, 'abs': abs,
    'pi': np.pi, 'e': np.e,
    'np': np,
    '__builtins__': {},
}


class CustomModel(IModel):
    """Пользовательская ODE-модель, задаваемая строковыми выражениями."""

    CATEGORY = "Пользовательские"

    def __init__(
        self,
        name: str,
        description: str,
        state_names: List[str],
        equations: List[str],
        parameters: List[Parameter],
        initial_conditions: Dict[str, float],
    ):
        if len(state_names) != len(equations):
            raise ValueError(
                f"Количество уравнений ({len(equations)}) "
                f"должно совпадать с количеством переменных ({len(state_names)})"
            )
        self._name = name
        self._description = description
        self._state_names = state_names
        self._equations = equations
        self._parameters = parameters
        self._initial_conditions = initial_conditions

    # --- IModel properties ---

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self.CATEGORY

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters

    @property
    def state_names(self) -> List[str]:
        return self._state_names

    # --- IModel methods ---

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([
            self._initial_conditions.get(n, 0.0)
            for n in self._state_names
        ], dtype=float)

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        ns = dict(_SAFE_MATH)
        ns['t'] = t
        for i, n in enumerate(self._state_names):
            ns[n] = float(state[i])
        ns.update({k: float(v) for k, v in params.items()})

        result = []
        for eq in self._equations:
            try:
                val = eval(eq, ns)  # noqa: S307
                result.append(float(val))
            except Exception as exc:
                raise RuntimeError(f"Ошибка в уравнении '{eq}': {exc}") from exc
        return np.array(result, dtype=float)

    def get_plot_config(self) -> PlotConfig:
        palette = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']
        return PlotConfig(
            title=self._name,
            xlabel="Время",
            ylabel="Значение",
            legend_labels=list(self._state_names),
            colors=palette[: len(self._state_names)],
        )

    def validate(self) -> bool:
        """Проверить, что уравнения выполняются при начальных условиях."""
        params = {p.name: p.default_value for p in self._parameters}
        state = self.get_initial_state(params)
        derivs = self.derivatives(0.0, state, params)
        return len(derivs) == len(self._state_names)
