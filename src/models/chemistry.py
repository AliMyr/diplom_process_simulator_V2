from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class FirstOrderReaction(BaseModel):
    """Реакция первого порядка: A → B. d[A]/dt = -k[A]"""

    _name = "Реакция первого порядка"
    _description = "Простейшая химическая реакция A → B. Скорость пропорциональна концентрации."

    _state_names = ["A", "B"]

    _parameters = [
        Parameter("k", "k (константа скорости)", 0.1, 0.001, 1.0, 0.01, "1/с"),
        Parameter("A0", "[A]₀ (нач. конц.)", 1.0, 0.1, 10.0, 0.1, "моль/л"),
        Parameter("B0", "[B]₀ (нач. конц.)", 0.0, 0.0, 10.0, 0.1, "моль/л"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["A0"], params["B0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        A, B = state
        k = params["k"]

        dA_dt = -k * A
        dB_dt = k * A

        return np.array([dA_dt, dB_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Реакция первого порядка",
            xlabel="Время (с)",
            ylabel="Концентрация (моль/л)",
            legend_labels=["[A] - реагент", "[B] - продукт"],
            colors=["#e74c3c", "#27ae60"],
            grid=True
        )


class ReversibleReaction(BaseModel):
    """Обратимая реакция: A ⇌ B. Устанавливается химическое равновесие."""

    _name = "Обратимая реакция"
    _description = "Реакция A ⇌ B. Прямая и обратная реакции устанавливают равновесие."

    _state_names = ["A", "B"]

    _parameters = [
        Parameter("k1", "k₁ (прямая)", 0.1, 0.001, 1.0, 0.01, "1/с"),
        Parameter("k2", "k₂ (обратная)", 0.05, 0.001, 1.0, 0.01, "1/с"),
        Parameter("A0", "[A]₀", 1.0, 0.0, 10.0, 0.1, "моль/л"),
        Parameter("B0", "[B]₀", 0.0, 0.0, 10.0, 0.1, "моль/л"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["A0"], params["B0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        A, B = state
        k1 = params["k1"]
        k2 = params["k2"]

        dA_dt = -k1 * A + k2 * B
        dB_dt = k1 * A - k2 * B

        return np.array([dA_dt, dB_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Обратимая реакция A ⇌ B",
            xlabel="Время (с)",
            ylabel="Концентрация (моль/л)",
            legend_labels=["[A]", "[B]"],
            colors=["#e74c3c", "#27ae60"],
            grid=True
        )


class Brusselator(BaseModel):
    """Брюсселятор — автоколебательная химическая система."""

    _name = "Брюсселятор"
    _description = "Модель автоколебательной реакции. При B > 1 + A² демонстрирует устойчивые колебания."

    _state_names = ["X", "Y"]

    _parameters = [
        Parameter("A", "A (поступление)", 1.0, 0.1, 5.0, 0.1, "моль/л"),
        Parameter("B", "B (катализатор)", 3.0, 0.1, 10.0, 0.1, "моль/л"),
        Parameter("X0", "[X]₀", 1.0, 0.0, 5.0, 0.1, "моль/л"),
        Parameter("Y0", "[Y]₀", 1.0, 0.0, 5.0, 0.1, "моль/л"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["X0"], params["Y0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        X, Y = state
        A = params["A"]
        B = params["B"]

        dX_dt = A + X**2 * Y - B * X - X
        dY_dt = B * X - X**2 * Y

        return np.array([dX_dt, dY_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Брюсселятор",
            xlabel="Время",
            ylabel="Концентрация",
            legend_labels=["[X]", "[Y]"],
            colors=["#e74c3c", "#3498db"],
            grid=True
        )