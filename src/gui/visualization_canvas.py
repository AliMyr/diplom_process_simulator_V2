from typing import List, Optional, Dict
import numpy as np

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSignal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..core.interfaces import SimulationResult, PlotConfig


class VisualizationCanvas(FigureCanvas):
    """Холст matplotlib — рисует графики."""

    point_clicked = pyqtSignal(float, float)

    def __init__(self, parent=None):
        # ВАЖНО: сначала создаём Figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.axes = self.fig.add_subplot(111)

        # ВАЖНО: вызываем super().__init__() с Figure
        super().__init__(self.fig)

        # ТОЛЬКО ПОТОМ устанавливаем родителя и другие свойства
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Теперь можем работать с событиями
        self.mpl_connect('button_press_event', self._on_click)

        # Для сравнения симуляций
        self.comparison_mode = False
        self.comparison_results: Dict[str, SimulationResult] = {}

        self._setup_axes()

    def _setup_axes(self):
        self.axes.set_xlabel('X')
        self.axes.set_ylabel('Y')
        self.axes.grid(True, alpha=0.3)
        self.fig.tight_layout()

    def _on_click(self, event):
        if event.inaxes == self.axes and event.xdata is not None:
            self.point_clicked.emit(event.xdata, event.ydata)

    def clear(self):
        self.axes.clear()
        self._setup_axes()
        self.draw()

    def plot_result(
            self,
            result: SimulationResult,
            config: PlotConfig,
            x_var: str = 'time',
            y_vars: Optional[List[str]] = None
    ):
        self.axes.clear()

        # Данные для оси X
        if x_var == 'time':
            x_data = result.time
        else:
            x_data = result.states[x_var]

        # Данные для оси Y
        if y_vars is None:
            y_vars = list(result.states.keys())

        default_colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6']

        for i, var_name in enumerate(y_vars):
            if var_name not in result.states:
                continue

            y_data = result.states[var_name]
            color = config.colors[i] if i < len(config.colors) else default_colors[i % len(default_colors)]
            label = config.legend_labels[i] if i < len(config.legend_labels) else var_name

            self.axes.plot(x_data, y_data, color=color, label=label, linewidth=1.5)

        self.axes.set_title(config.title, fontsize=12, fontweight='bold')
        self.axes.set_xlabel(config.xlabel, fontsize=10)
        self.axes.set_ylabel(config.ylabel, fontsize=10)
        self.axes.grid(config.grid, alpha=0.3)

        if len(y_vars) > 1:
            self.axes.legend(loc='best', fontsize=9)

        self.fig.tight_layout()
        self.draw()

    def plot_phase_portrait(
            self,
            result: SimulationResult,
            x_var: str,
            y_var: str,
            title: str = "Фазовый портрет"
    ):
        self.axes.clear()

        x_data = result.states[x_var]
        y_data = result.states[y_var]

        self.axes.plot(x_data, y_data, 'b-', linewidth=1.5, label='Траектория')
        self.axes.plot(x_data[0], y_data[0], 'go', markersize=10, label='Начало')
        self.axes.plot(x_data[-1], y_data[-1], 'ro', markersize=8, label='Конец')

        self.axes.set_title(title, fontsize=12, fontweight='bold')
        self.axes.set_xlabel(x_var, fontsize=10)
        self.axes.set_ylabel(y_var, fontsize=10)
        self.axes.grid(True, alpha=0.3)
        self.axes.legend(loc='best', fontsize=9)

        self.fig.tight_layout()
        self.draw()

    def plot_comparison(self, results: Dict[str, SimulationResult],
                        config: PlotConfig, var_name: str):
        """Построить сравнение нескольких симуляций для одной переменной."""
        self.axes.clear()

        colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']

        for idx, (label, result) in enumerate(results.items()):
            if var_name not in result.states:
                continue

            color = colors[idx % len(colors)]
            self.axes.plot(
                result.time,
                result.states[var_name],
                label=label,
                color=color,
                linewidth=2,
                alpha=0.8
            )

        self.axes.set_title(f"Сравнение: {var_name}", fontsize=12, fontweight='bold')
        self.axes.set_xlabel(config.xlabel, fontsize=10)
        self.axes.set_ylabel(var_name, fontsize=10)
        self.axes.grid(True, alpha=0.3)
        self.axes.legend(loc='best', fontsize=9)

        self.fig.tight_layout()
        self.draw()

    def add_comparison_result(self, name: str, result: SimulationResult):
        """Добавить результат для сравнения."""
        self.comparison_results[name] = result

    def clear_comparison(self):
        """Очистить результаты сравнения."""
        self.comparison_results.clear()

    def get_comparison_results(self) -> Dict[str, SimulationResult]:
        """Получить все результаты сравнения."""
        return self.comparison_results

    def save_figure(self, filepath: str, dpi: int = 150):
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight')


class VisualizationWidget(QWidget):
    """Виджет с холстом и панелью инструментов."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = VisualizationCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def plot_result(self, result: SimulationResult, config: PlotConfig, **kwargs):
        self.canvas.plot_result(result, config, **kwargs)

    def plot_phase_portrait(self, result: SimulationResult, x_var: str, y_var: str, **kwargs):
        self.canvas.plot_phase_portrait(result, x_var, y_var, **kwargs)

    def plot_comparison(self, results: Dict[str, SimulationResult],
                        config: PlotConfig, var_name: str):
        self.canvas.plot_comparison(results, config, var_name)

    def clear(self):
        self.canvas.clear()

    def save_figure(self, filepath: str, **kwargs):
        self.canvas.save_figure(filepath, **kwargs)