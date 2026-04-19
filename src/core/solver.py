from typing import Callable, Optional, Tuple
import numpy as np
from scipy.integrate import solve_ivp

from .interfaces import ISolver


class ScipySolver(ISolver):
    """Решатель на основе scipy — точный, рекомендуемый."""

    def __init__(self, method: str = 'RK45', rtol: float = 1e-6, atol: float = 1e-9):
        self._method = method
        self._rtol = rtol
        self._atol = atol

    def solve(
        self,
        derivatives: Callable[[float, np.ndarray], np.ndarray],
        initial_state: np.ndarray,
        t_span: Tuple[float, float],
        t_eval: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:

        solution = solve_ivp(
            derivatives,
            t_span,
            initial_state,
            method=self._method,
            t_eval=t_eval,
            rtol=self._rtol,
            atol=self._atol
        )

        if not solution.success:
            raise RuntimeError(f"Решатель не сошёлся: {solution.message}")

        return solution.t, solution.y


class SolverFactory:
    """Фабрика решателей — чтобы не создавать вручную."""

    _solvers = {
        'scipy': ScipySolver,
    }

    @classmethod
    def create(cls, solver_type: str = 'scipy', **kwargs) -> ISolver:
        if solver_type not in cls._solvers:
            raise ValueError(f"Неизвестный решатель: {solver_type}")
        return cls._solvers[solver_type](**kwargs)