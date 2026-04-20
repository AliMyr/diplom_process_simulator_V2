import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..core.interfaces import SimulationResult


class WorkspacePanel(QWidget):
    """Браузер переменных рабочего пространства (как MATLAB Workspace)."""

    COLUMNS = ["Имя", "Размер", "Тип", "Мин", "Макс", "Среднее", "Ст.откл."]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: SimulationResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        title = QLabel("Рабочее пространство")
        title.setStyleSheet("font-weight: bold; font-size: 11px;")
        header_row.addWidget(title)
        header_row.addStretch()
        clear_btn = QPushButton("Очистить")
        clear_btn.setFixedWidth(75)
        clear_btn.setStyleSheet("padding: 3px 8px;")
        clear_btn.clicked.connect(self.clear)
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setFont(QFont("Consolas, Courier New, monospace", 9))
        layout.addWidget(self.table)

        self.status_label = QLabel("Нет данных")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 2px;")
        layout.addWidget(self.status_label)

    def update_result(self, result: SimulationResult):
        self._result = result
        self.table.setRowCount(0)

        self._add_variable("t", result.time, "time array")
        for name, arr in result.states.items():
            self._add_variable(name, arr, "state")

        meta = result.metadata
        model_name = meta.get('model', 'N/A')
        solver = meta.get('solver', 'RK45')
        n = len(result.time)
        t0 = result.time[0]
        t1 = result.time[-1]
        self.status_label.setText(
            f"Модель: {model_name}  |  Решатель: {solver}  |  "
            f"Точек: {n}  |  t ∈ [{t0:.3f}, {t1:.3f}]"
        )

    def _add_variable(self, name: str, arr: np.ndarray, kind: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        cells = [
            name,
            f"1×{len(arr)}",
            kind,
            f"{arr.min():.6g}",
            f"{arr.max():.6g}",
            f"{arr.mean():.6g}",
            f"{arr.std():.6g}",
        ]
        for col, text in enumerate(cells):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col == 0:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, col, item)

    def clear(self):
        self.table.setRowCount(0)
        self.status_label.setText("Нет данных")
        self._result = None
