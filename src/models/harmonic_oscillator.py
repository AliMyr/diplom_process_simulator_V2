from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class HarmonicOscillator(BaseModel):
    """Гармонический осциллятор с затуханием. m*x'' + γ*x' + k*x = 0"""

    _name = "Гармонический осциллятор"
    _description = "Колебания тела на пружине с затуханием."

    _state_names = ["x", "v"]

    _parameters = [
        Parameter("m", "Масса (кг)", 1.0, 0.1, 10.0, 0.1, "кг"),
        Parameter("k", "Жёсткость (Н/м)", 10.0, 0.1, 100.0, 0.5, "Н/м"),
        Parameter("gamma", "Затухание", 0.5, 0.0, 5.0, 0.1, "кг/с"),
        Parameter("x0", "Нач. положение (м)", 1.0, -5.0, 5.0, 0.1, "м"),
        Parameter("v0", "Нач. скорость (м/с)", 0.0, -10.0, 10.0, 0.1, "м/с"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["x0"], params["v0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        x, v = state
        m = params["m"]
        k = params["k"]
        gamma = params["gamma"]

        dx_dt = v
        dv_dt = (-gamma * v - k * x) / m

        return np.array([dx_dt, dv_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Гармонический осциллятор",
            xlabel="Время (с)",
            ylabel="Значение",
            legend_labels=["Координата x (м)", "Скорость v (м/с)"],
            colors=["#2ecc71", "#e74c3c"],
            grid=True
        )