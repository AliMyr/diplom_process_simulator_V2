from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class NewtonCooling(BaseModel):
    """Закон охлаждения Ньютона. dT/dt = -k(T - T_env)"""

    _name = "Закон охлаждения Ньютона"
    _description = "Температура тела экспоненциально приближается к температуре среды."

    _state_names = ["T"]

    _parameters = [
        Parameter("k", "k (коэф. теплообмена)", 0.1, 0.01, 1.0, 0.01, "1/мин"),
        Parameter("T0", "T₀ (нач. температура)", 100.0, -50.0, 200.0, 1.0, "°C"),
        Parameter("T_env", "T_env (температура среды)", 20.0, -50.0, 50.0, 1.0, "°C"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["T0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        T = state[0]
        k = params["k"]
        T_env = params["T_env"]

        dT_dt = -k * (T - T_env)

        return np.array([dT_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Закон охлаждения Ньютона",
            xlabel="Время (мин)",
            ylabel="Температура (°C)",
            legend_labels=["Температура тела"],
            colors=["#e74c3c"],
            grid=True
        )


class RLCCircuit(BaseModel):
    """RLC-контур. L*dI/dt + R*I + q/C = 0"""

    _name = "RLC-контур"
    _description = "Колебательный контур. При малом R — затухающие колебания."

    _state_names = ["q", "I"]

    _parameters = [
        Parameter("R", "R (Ом)", 10.0, 0.0, 1000.0, 1.0, "Ом"),
        Parameter("L", "L (Гн)", 0.1, 0.001, 10.0, 0.01, "Гн"),
        Parameter("C", "C (Ф)", 0.001, 1e-6, 0.1, 0.0001, "Ф"),
        Parameter("q0", "q₀ (нач. заряд, Кл)", 0.001, 0.0, 0.01, 0.0001, "Кл"),
        Parameter("I0", "I₀ (нач. ток, А)", 0.0, -1.0, 1.0, 0.01, "А"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["q0"], params["I0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        q, I = state
        R = params["R"]
        L = params["L"]
        C = params["C"]

        # Защита от деления на ноль
        if L < 1e-10 or C < 1e-10:
            return np.array([0.0, 0.0])

        dq_dt = I
        dI_dt = (-R * I - q / C) / L

        return np.array([dq_dt, dI_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="RLC-контур",
            xlabel="Время (с)",
            ylabel="Значение",
            legend_labels=["Заряд q (Кл)", "Ток I (А)"],
            colors=["#3498db", "#e74c3c"],
            grid=True
        )


class ThermalMass(BaseModel):
    """Нагрев тела с учётом теплоёмкости. m*c*dT/dt = P - hA*(T - T_env)"""

    _name = "Нагрев с теплоёмкостью"
    _description = "Нагрев тела внешним источником с теплопотерями в среду."

    _state_names = ["T"]

    _parameters = [
        Parameter("m", "Масса (кг)", 1.0, 0.1, 100.0, 0.1, "кг"),
        Parameter("c", "Теплоёмкость (Дж/(кг·К))", 4186.0, 100.0, 10000.0, 100.0, "Дж/(кг·К)"),
        Parameter("P", "Мощность (Вт)", 1000.0, 0.0, 10000.0, 100.0, "Вт"),
        Parameter("hA", "h·A (теплоотдача)", 10.0, 0.0, 100.0, 1.0, "Вт/К"),
        Parameter("T0", "T₀ (нач. температура)", 20.0, -50.0, 200.0, 1.0, "°C"),
        Parameter("T_env", "T_env (температура среды)", 20.0, -50.0, 50.0, 1.0, "°C"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["T0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        T = state[0]
        m = params["m"]
        c = params["c"]
        P = params["P"]
        hA = params["hA"]
        T_env = params["T_env"]

        dT_dt = (P - hA * (T - T_env)) / (m * c)

        return np.array([dT_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Нагрев тела",
            xlabel="Время (с)",
            ylabel="Температура (°C)",
            legend_labels=["Температура"],
            colors=["#e74c3c"],
            grid=True
        )