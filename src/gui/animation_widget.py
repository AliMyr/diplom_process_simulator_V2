import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.interfaces import SimulationResult


class AnimationWidget(QWidget):
    """Виджет анимации симуляции в фазовом пространстве."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: SimulationResult | None = None
        self._frame = 0
        self._is_playing = False
        self._timer = QTimer()
        self._timer.timeout.connect(self._next_frame)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Variable selectors
        var_group = QGroupBox("Оси анимации")
        var_layout = QHBoxLayout(var_group)
        var_layout.addWidget(QLabel("X:"))
        self.x_combo = QComboBox()
        self.x_combo.currentTextChanged.connect(lambda _: self._redraw_current())
        var_layout.addWidget(self.x_combo)
        var_layout.addWidget(QLabel("Y:"))
        self.y_combo = QComboBox()
        self.y_combo.currentTextChanged.connect(lambda _: self._redraw_current())
        var_layout.addWidget(self.y_combo)
        var_layout.addWidget(QLabel("Скорость:"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 120)
        self.speed_spin.setValue(30)
        self.speed_spin.setSuffix(" fps")
        self.speed_spin.valueChanged.connect(self._update_timer_interval)
        var_layout.addWidget(self.speed_spin)
        var_layout.addStretch()
        layout.addWidget(var_group)

        # Figure
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Frame slider
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setRange(0, 100)
        self.frame_slider.valueChanged.connect(self._on_slider)
        layout.addWidget(self.frame_slider)

        # Playback controls
        ctrl = QHBoxLayout()
        self.play_btn = QPushButton("▶ Воспроизвести")
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; padding: 8px 16px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.play_btn.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_btn)

        stop_btn = QPushButton("⏹ В начало")
        stop_btn.setStyleSheet("padding: 8px 12px; border-radius: 4px;")
        stop_btn.clicked.connect(self._rewind)
        ctrl.addWidget(stop_btn)

        self.time_label = QLabel("t = 0.0000")
        self.time_label.setStyleSheet("font-family: monospace; font-size: 13px; padding: 0 12px;")
        ctrl.addWidget(self.time_label)

        self.frame_label = QLabel("0 / 0")
        self.frame_label.setStyleSheet("color: #666; font-size: 11px;")
        ctrl.addWidget(self.frame_label)
        ctrl.addStretch()
        layout.addLayout(ctrl)

    def set_result(self, result: SimulationResult):
        self._result = result
        self._frame = 0
        self._stop_timer()

        vars_list = list(result.states.keys())
        for combo in (self.x_combo, self.y_combo):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(vars_list)
            combo.blockSignals(False)
        if len(vars_list) >= 2:
            self.y_combo.setCurrentIndex(1)

        self.frame_slider.blockSignals(True)
        self.frame_slider.setRange(0, len(result.time) - 1)
        self.frame_slider.setValue(0)
        self.frame_slider.blockSignals(False)
        self._draw_frame(0)

    def _toggle_play(self):
        if self._is_playing:
            self._stop_timer()
        else:
            if self._result and self._frame >= len(self._result.time) - 1:
                self._frame = 0
            self._is_playing = True
            self._timer.start(1000 // max(1, self.speed_spin.value()))
            self.play_btn.setText("⏸ Пауза")

    def _stop_timer(self):
        self._is_playing = False
        self._timer.stop()
        self.play_btn.setText("▶ Воспроизвести")

    def _rewind(self):
        self._stop_timer()
        self._frame = 0
        self.frame_slider.setValue(0)
        if self._result:
            self._draw_frame(0)

    def _next_frame(self):
        if self._result is None:
            return
        self._frame += 1
        if self._frame >= len(self._result.time):
            self._frame = len(self._result.time) - 1
            self._stop_timer()
            return
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(self._frame)
        self.frame_slider.blockSignals(False)
        self._draw_frame(self._frame)

    def _on_slider(self, value: int):
        self._frame = value
        if self._result:
            self._draw_frame(value)

    def _update_timer_interval(self):
        if self._is_playing:
            self._timer.setInterval(1000 // max(1, self.speed_spin.value()))

    def _redraw_current(self):
        if self._result:
            self._draw_frame(self._frame)

    def _draw_frame(self, idx: int):
        if self._result is None:
            return
        x_var = self.x_combo.currentText()
        y_var = self.y_combo.currentText()
        if not x_var or not y_var:
            return
        states = self._result.states
        if x_var not in states or y_var not in states:
            return

        x_all = states[x_var]
        y_all = states[y_var]
        t = self._result.time[idx]
        n = len(self._result.time)

        self.ax.clear()
        self.ax.plot(x_all, y_all, color='#bdc3c7', linewidth=1, alpha=0.4, zorder=1)
        self.ax.plot(x_all[:idx + 1], y_all[:idx + 1], color='#3498db', linewidth=2, zorder=2)
        self.ax.plot(x_all[idx], y_all[idx], 'o', color='#e74c3c', markersize=12, zorder=5,
                     label=f't = {t:.3f}')

        self.ax.set_title(f"Анимация: {x_var} vs {y_var}", fontsize=12, fontweight='bold')
        self.ax.set_xlabel(x_var, fontsize=10)
        self.ax.set_ylabel(y_var, fontsize=10)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right', fontsize=9)

        self.fig.tight_layout()
        self.canvas.draw()

        self.time_label.setText(f"t = {t:.4f}")
        self.frame_label.setText(f"{idx + 1} / {n}")

    def save_figure(self, filepath: str):
        self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
