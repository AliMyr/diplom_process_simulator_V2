from __future__ import annotations

import time as _time
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QGroupBox, QTextEdit
)
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp

from ..core.interfaces import IModel, SimulationResult


_METHODS: dict[str, str] = {
    'RK45':   'Runge-Kutta 4(5) — универсальный',
    'RK23':   'Runge-Kutta 2(3) — быстрый, менее точный',
    'DOP853': 'DOP853 8-й порядок — высокая точность',
    'Radau':  'Radau — для жёстких СДУ',
    'BDF':    'BDF — для жёстких СДУ',
    'LSODA':  'LSODA — адаптивный (жёсткие/нежёсткие)',
}

_COLORS = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']


class SolverComparisonWidget(QWidget):
    """Сравнение численных методов решения ОДУ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model: IModel | None = None
        self._params: dict | None = None
        self._t_start = 0.0
        self._t_end = 10.0
        self._num_points = 1000
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Variable selector + run button
        top = QHBoxLayout()
        top.addWidget(QLabel("Переменная:"))
        self.var_combo = QComboBox()
        top.addWidget(self.var_combo)
        top.addStretch()
        run_btn = QPushButton("▶ Запустить сравнение")
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9; color: white;
                font-weight: bold; padding: 7px 16px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #3498db; }
        """)
        run_btn.clicked.connect(self._run)
        top.addWidget(run_btn)
        layout.addLayout(top)

        # Method checkboxes
        methods_group = QGroupBox("Методы решения")
        methods_layout = QHBoxLayout(methods_group)
        self._checks: dict[str, QCheckBox] = {}
        for i, (method, label) in enumerate(_METHODS.items()):
            cb = QCheckBox(method)
            cb.setToolTip(label)
            cb.setChecked(i < 3)
            methods_layout.addWidget(cb)
            self._checks[method] = cb
        layout.addWidget(methods_group)

        # Figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Log output
        mono = QFont("Consolas", 9)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(mono)
        self.log.setMaximumHeight(90)
        self.log.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")
        layout.addWidget(self.log)

    # ------------------------------------------------------------------
    def set_simulation_params(
        self,
        model: IModel,
        params: dict,
        t_start: float,
        t_end: float,
        num_points: int,
    ):
        self._model = model
        self._params = params
        self._t_start = t_start
        self._t_end = t_end
        self._num_points = num_points

        state_names = list(model.state_names)
        self.var_combo.blockSignals(True)
        self.var_combo.clear()
        self.var_combo.addItems(state_names)
        self.var_combo.blockSignals(False)

    def _run(self):
        if self._model is None or self._params is None:
            self.log.setText("Сначала запустите основную симуляцию.")
            return

        var_name = self.var_combo.currentText()
        if not var_name:
            return

        try:
            var_idx = list(self._model.state_names).index(var_name)
        except ValueError:
            return

        t_eval = np.linspace(self._t_start, self._t_end, self._num_points)
        initial = self._model.get_initial_state(self._params)

        def deriv(t, y):
            return self._model.derivatives(t, y, self._params)

        self.ax.clear()
        log_lines: list[str] = []

        color_idx = 0
        for method, cb in self._checks.items():
            if not cb.isChecked():
                continue
            t0 = _time.perf_counter()
            try:
                sol = solve_ivp(
                    deriv,
                    [self._t_start, self._t_end],
                    initial,
                    method=method,
                    t_eval=t_eval,
                    rtol=1e-6,
                    atol=1e-9,
                    dense_output=False,
                )
                elapsed_ms = (_time.perf_counter() - t0) * 1000
                if sol.success:
                    color = _COLORS[color_idx % len(_COLORS)]
                    self.ax.plot(
                        sol.t, sol.y[var_idx],
                        label=f"{method} ({elapsed_ms:.1f}мс)",
                        color=color,
                        linewidth=2,
                        alpha=0.85,
                    )
                    log_lines.append(
                        f"{method:8s}: {elapsed_ms:7.2f}мс  |  "
                        f"шагов: {sol.t_events[0].size if sol.t_events else 'N/A':>5}  |  "
                        f"вычислений f: {sol.nfev}"
                    )
                else:
                    log_lines.append(f"{method:8s}: ОШИБКА — {sol.message}")
            except Exception as exc:
                elapsed_ms = (_time.perf_counter() - t0) * 1000
                log_lines.append(f"{method:8s}: исключение ({elapsed_ms:.1f}мс) — {exc}")
            color_idx += 1

        self.ax.set_title(
            f"Сравнение решателей: {var_name}",
            fontsize=12, fontweight='bold'
        )
        self.ax.set_xlabel("Время", fontsize=10)
        self.ax.set_ylabel(var_name, fontsize=10)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(fontsize=9)
        self.fig.tight_layout()
        self.canvas.draw()

        self.log.setText('\n'.join(log_lines))

    def save_figure(self, filepath: str):
        self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
