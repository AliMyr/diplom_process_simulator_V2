import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..core.interfaces import SimulationResult


class FFTWidget(QWidget):
    """Анализ Фурье / спектральный анализ результатов симуляции."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: SimulationResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Переменная:"))
        self.var_combo = QComboBox()
        self.var_combo.currentTextChanged.connect(self._update_plot)
        controls.addWidget(self.var_combo)

        self.log_scale_cb = QCheckBox("Лог. масштаб Y")
        self.log_scale_cb.toggled.connect(self._update_plot)
        controls.addWidget(self.log_scale_cb)

        self.show_peaks_cb = QCheckBox("Показать пики")
        self.show_peaks_cb.setChecked(True)
        self.show_peaks_cb.toggled.connect(self._update_plot)
        controls.addWidget(self.show_peaks_cb)

        controls.addStretch()
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        controls.addWidget(self.info_label)
        layout.addLayout(controls)

        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def set_result(self, result: SimulationResult):
        self._result = result
        self.var_combo.blockSignals(True)
        self.var_combo.clear()
        self.var_combo.addItems(list(result.states.keys()))
        self.var_combo.blockSignals(False)
        self._update_plot()

    def _update_plot(self):
        if self._result is None:
            return

        var = self.var_combo.currentText()
        if not var or var not in self._result.states:
            return

        signal = self._result.states[var]
        n = len(signal)
        if n < 4:
            return

        dt = (self._result.time[-1] - self._result.time[0]) / (n - 1)
        fft_vals = np.abs(np.fft.rfft(signal - signal.mean())) * 2 / n
        freqs = np.fft.rfftfreq(n, d=dt)

        # Skip DC
        fft_vals = fft_vals[1:]
        freqs = freqs[1:]

        self.ax.clear()
        self.ax.fill_between(freqs, fft_vals, alpha=0.3, color='#3498db')
        self.ax.plot(freqs, fft_vals, '#3498db', linewidth=1.2)

        if self.show_peaks_cb.isChecked() and len(fft_vals) > 0:
            try:
                from scipy.signal import find_peaks
                peaks, props = find_peaks(fft_vals, height=fft_vals.max() * 0.1, distance=3)
                if len(peaks) > 0:
                    top_peaks = sorted(peaks, key=lambda i: fft_vals[i], reverse=True)[:5]
                    for pk in top_peaks:
                        self.ax.axvline(x=freqs[pk], color='#e74c3c', linestyle='--', alpha=0.6, linewidth=1)
                        self.ax.annotate(
                            f'{freqs[pk]:.3f}',
                            xy=(freqs[pk], fft_vals[pk]),
                            xytext=(5, 5), textcoords='offset points',
                            fontsize=8, color='#e74c3c'
                        )
                    dominant_freq = freqs[top_peaks[0]]
                    period = 1.0 / dominant_freq if dominant_freq > 0 else float('inf')
                    self.info_label.setText(
                        f"Доминирующая: {dominant_freq:.4f} Гц  |  Период: {period:.4f}"
                    )
            except Exception:
                pass

        self.ax.set_title(f"Спектр Фурье: {var}", fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Частота (Гц)", fontsize=10)
        self.ax.set_ylabel("Амплитуда", fontsize=10)
        self.ax.grid(True, alpha=0.3)

        if self.log_scale_cb.isChecked():
            self.ax.set_yscale('log')

        self.fig.tight_layout()
        self.canvas.draw()

    def save_figure(self, filepath: str):
        self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
