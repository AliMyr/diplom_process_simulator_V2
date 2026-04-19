from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class Pendulum(BaseModel):
    """Математический маятник с затуханием. θ'' + (γ/m)*θ' + (g/L)*sin(θ) = 0"""

    _name = "Математический маятник"
    _description = "Нелинейный маятник с затуханием."

    _state_names = ["theta", "omega"]

    _parameters = [
        Parameter("L", "Длина (м)", 1.0, 0.1, 5.0, 0.1, "м"),
        Parameter("m", "Масса (кг)", 1.0, 0.1, 10.0, 0.1, "кг"),
        Parameter("g", "Ускорение (м/с²)", 9.81, 1.0, 25.0, 0.1, "м/с²"),
        Parameter("gamma", "Затухание", 0.1, 0.0, 2.0, 0.05, "кг/с"),
        Parameter("theta0", "Нач. угол (рад)", 0.5, -3.14, 3.14, 0.1, "рад"),
        Parameter("omega0", "Нач. скорость (рад/с)", 0.0, -10.0, 10.0, 0.1, "рад/с"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["theta0"], params["omega0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        theta, omega = state
        L = params["L"]
        m = params["m"]
        g = params["g"]
        gamma = params["gamma"]

        dtheta_dt = omega
        domega_dt = -(g / L) * np.sin(theta) - (gamma / m) * omega

        return np.array([dtheta_dt, domega_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Математический маятник",
            xlabel="Время (с)",
            ylabel="Значение",
            legend_labels=["Угол θ (рад)", "Угловая скорость ω (рад/с)"],
            colors=["#3498db", "#9b59b6"],
            grid=True
        )