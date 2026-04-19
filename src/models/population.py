from typing import Dict
import numpy as np

from ..core.interfaces import Parameter, PlotConfig
from .base_model import BaseModel


class LotkaVolterra(BaseModel):
    """Хищник-жертва. dx/dt = αx - βxy, dy/dt = δxy - γy"""

    _name = "Хищник-жертва (Лотка-Вольтерра)"
    _description = "Циклическая динамика двух популяций."

    _state_names = ["prey", "predator"]

    _parameters = [
        Parameter("alpha", "α (размножение жертв)", 1.0, 0.1, 5.0, 0.1, "1/время"),
        Parameter("beta", "β (эффект. охоты)", 0.1, 0.01, 1.0, 0.01, "1/(особь·время)"),
        Parameter("gamma", "γ (смертность хищников)", 1.5, 0.1, 5.0, 0.1, "1/время"),
        Parameter("delta", "δ (конверсия)", 0.075, 0.01, 0.5, 0.01, "1/(особь·время)"),
        Parameter("x0", "Нач. числ. жертв", 40.0, 1.0, 200.0, 1.0, "особей"),
        Parameter("y0", "Нач. числ. хищников", 9.0, 1.0, 100.0, 1.0, "особей"),
    ]

    def get_initial_state(self, params: Dict[str, float]) -> np.ndarray:
        return np.array([params["x0"], params["y0"]])

    def derivatives(self, t: float, state: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        x, y = state
        alpha = params["alpha"]
        beta = params["beta"]
        gamma = params["gamma"]
        delta = params["delta"]

        dx_dt = alpha * x - beta * x * y
        dy_dt = delta * x * y - gamma * y

        return np.array([dx_dt, dy_dt])

    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            title="Хищник-жертва",
            xlabel="Время",
            ylabel="Численность",
            legend_labels=["Жертвы", "Хищники"],
            colors=["#27ae60", "#c0392b"],
            grid=True
        )