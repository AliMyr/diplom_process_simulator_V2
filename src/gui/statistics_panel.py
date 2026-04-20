import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
)
from PyQt6.QtGui import QFont

from ..core.interfaces import SimulationResult


class StatisticsPanel(QWidget):
    """Панель детальной статистики результатов симуляции."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: SimulationResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        toolbar = QHBoxLayout()
        title = QLabel("Статистика симуляции")
        title.setStyleSheet("font-weight: bold; font-size: 11px;")
        toolbar.addWidget(title)
        toolbar.addStretch()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setFixedWidth(80)
        refresh_btn.setStyleSheet("padding: 3px 8px;")
        refresh_btn.clicked.connect(self._render)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        mono = QFont("Consolas", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(mono)
        self.text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.text)

    def update_result(self, result: SimulationResult):
        self._result = result
        self._render()

    def _render(self):
        if self._result is None:
            self.text.setText("Нет данных.")
            return

        r = self._result
        n = len(r.time)
        dt = (r.time[-1] - r.time[0]) / (n - 1) if n > 1 else 0
        model_name = r.metadata.get('model', 'N/A')
        solver = r.metadata.get('solver', 'RK45')

        lines: list[str] = []
        sep = '═' * 52
        lines += [
            sep,
            '  СТАТИСТИКА СИМУЛЯЦИИ',
            sep,
            f'  Модель:       {model_name}',
            f'  Решатель:     {solver}',
            f'  Точки:        {n}',
            f'  t_start:      {r.time[0]:.6g}',
            f'  t_end:        {r.time[-1]:.6g}',
            f'  dt:           {dt:.6g}',
            sep,
        ]

        for var_name, values in r.states.items():
            lines.append(f'\n  ▸ {var_name}')
            lines.append(f'    {"Мин:":<14} {values.min():.10g}')
            lines.append(f'    {"Макс:":<14} {values.max():.10g}')
            lines.append(f'    {"Среднее:":<14} {values.mean():.10g}')
            lines.append(f'    {"Ст.откл.:":<14} {values.std():.10g}')
            lines.append(f'    {"Медиана:":<14} {np.median(values):.10g}')
            lines.append(f'    {"Размах:":<14} {values.max() - values.min():.10g}')
            lines.append(f'    {"RMS:":<14} {np.sqrt(np.mean(values ** 2)):.10g}')

            try:
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(values, height=values.mean())
                if len(peaks) >= 2:
                    periods = np.diff(r.time[peaks])
                    mean_p = np.mean(periods)
                    lines.append(f'    {"Период:":<14} {mean_p:.8g}')
                    lines.append(f'    {"Частота:":<14} {1.0 / mean_p:.8g} Гц')
                    lines.append(f'    {"Пиков:":<14} {len(peaks)}')
            except Exception:
                pass

        lines.append(f'\n{sep}')
        self.text.setText('\n'.join(lines))
