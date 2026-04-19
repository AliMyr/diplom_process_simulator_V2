from typing import Dict, List
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class ProjectileMotion(BaseModel):
    """Баллистическое движение. Гравитация + сопротивление воздуха."""

    _name = "Баллистика (бросок тела)"
    _description = "Движение брошенного тела в поле тяжести с учётом сопротивления воздуха."

    # Все 4 нужны решателю для вычисления производных
    _state_names = ["x", "y", "vx", "vy"]

    # Только эти два отображаются на графике траектории
    trajectory_vars = ["x", "y"]

    _parameters = [
        Parameter("v0", "Нач. скорость (м/с)", 20.0, 1.0, 100.0, 1.0, "м/с"),
        Parameter("angle", "Угол броска (°)", 45.0, 0.0, 90.0, 1.0, "°"),
        Parameter("g", "Ускорение (м/с²)", 9.81, 1.0, 25.0, 0.1, "м/с²"),
        Parameter("m", "Масса (кг)", 1.0, 0.01, 10.0, 0.1, "кг"),
        Parameter("Cd", "Коэф. сопротивления", 0.0, 0.0, 1.0, 0.01, ""),
        Parameter("y0", "Нач. высота (м)", 0.0, 0.0, 100.0, 1.0, "м"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        v0 = params["v0"]
        angle_rad = np.radians(params["angle"])
        return np.array([
            0.0,
            params["y0"],
            v0 * np.cos(angle_rad),
            v0 * np.sin(angle_rad)
        ])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        x, y, vx, vy = state
        g = params["g"]
        m = params["m"]
        Cd = params["Cd"]

        v = np.sqrt(vx**2 + vy**2)

        if Cd > 0 and v > 0:
            F_drag = 0.5 * Cd * 1.225 * 0.01 * v**2
            ax = -F_drag * vx / (m * v)
            ay = -F_drag * vy / (m * v)
        else:
            ax = 0.0
            ay = 0.0

        return np.array([vx, vy, ax, -g + ay])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Баллистическое движение",
            xlabel="Время (с)",
            ylabel="Значение",
            legend_labels=["y (м)", "vx (м/с)", "vy (м/с)"],
            colors=["#e74c3c", "#27ae60", "#f39c12"],
            grid=True
        )