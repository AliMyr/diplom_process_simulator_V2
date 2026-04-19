from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class SIRModel(BaseModel):
    """SIR модель эпидемии. dS/dt = -βSI/N, dI/dt = βSI/N - γI, dR/dt = γI"""

    _name = "SIR (эпидемиология)"
    _description = "Базовая модель распространения инфекции."

    _state_names = ["S", "I", "R"]

    _parameters = [
        Parameter("N", "Население", 1000.0, 100.0, 100000.0, 100.0, "человек"),
        Parameter("beta", "β (заражение)", 0.3, 0.01, 1.0, 0.01, "1/день"),
        Parameter("gamma", "γ (выздоровление)", 0.1, 0.01, 0.5, 0.01, "1/день"),
        Parameter("I0", "Нач. инфицированных", 1.0, 1.0, 100.0, 1.0, "человек"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        N = params["N"]
        I0 = params["I0"]
        S0 = N - I0
        return np.array([S0, I0, 0.0])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        S, I, R = state
        N = params["N"]
        beta = params["beta"]
        gamma = params["gamma"]

        dS_dt = -beta * S * I / N
        dI_dt = beta * S * I / N - gamma * I
        dR_dt = gamma * I

        return np.array([dS_dt, dI_dt, dR_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Модель SIR",
            xlabel="Время (дни)",
            ylabel="Численность",
            legend_labels=["Восприимчивые (S)", "Инфицированные (I)", "Выздоровевшие (R)"],
            colors=["#3498db", "#e74c3c", "#27ae60"],
            grid=True
        )