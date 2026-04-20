from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QGroupBox, QMessageBox, QGridLayout, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..core.interfaces import Parameter
from ..models.custom_model import CustomModel


_VAN_DER_POL = dict(
    name="Осциллятор ван дер Поля",
    description="Нелинейный осциллятор: d²x/dt² − μ(1−x²)ẋ + x = 0",
    state_vars="x, y",
    equations="y\nmu * (1 - x**2) * y - x",
    initial_conds="x = 2.0\ny = 0.0",
    params=[("mu", "μ (нелинейность)", "1.0", "0.1", "5.0")],
)

_LORENZ = dict(
    name="Аттрактор Лоренца",
    description="Хаотическая система: dx/dt = σ(y−x), dy/dt = x(ρ−z)−y, dz/dt = xy−βz",
    state_vars="x, y, z",
    equations="sigma * (y - x)\nx * (rho - z) - y\nx * y - beta * z",
    initial_conds="x = 1.0\ny = 1.0\nz = 1.0",
    params=[
        ("sigma", "σ (Прандтль)", "10.0", "1.0", "30.0"),
        ("rho", "ρ (Рэлей)", "28.0", "1.0", "50.0"),
        ("beta", "β", "2.667", "0.1", "10.0"),
    ],
)

_DUFFING = dict(
    name="Осциллятор Дуффинга",
    description="Нелинейный осциллятор: ẍ + δẋ + αx + βx³ = γcos(ωt)",
    state_vars="x, v",
    equations="v\n-delta * v - alpha * x - beta * x**3 + gamma * cos(omega * t)",
    initial_conds="x = 0.5\nv = 0.0",
    params=[
        ("alpha", "α (линейная жёсткость)", "1.0", "-2.0", "2.0"),
        ("beta", "β (нелинейная жёсткость)", "1.0", "-2.0", "5.0"),
        ("delta", "δ (затухание)", "0.2", "0.0", "2.0"),
        ("gamma", "γ (амплитуда)", "0.3", "0.0", "2.0"),
        ("omega", "ω (частота)", "1.2", "0.1", "5.0"),
    ],
)

EXAMPLES = {
    "Ван дер Поль": _VAN_DER_POL,
    "Лоренц": _LORENZ,
    "Дуффинг": _DUFFING,
}


class CustomModelDialog(QDialog):
    """Диалог создания пользовательской ODE-модели."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конструктор пользовательской модели")
        self.setMinimumSize(740, 640)
        self._model: CustomModel | None = None
        self._setup_ui()
        self._load_example(_VAN_DER_POL)

    def _setup_ui(self):
        root = QVBoxLayout(self)

        # Top: name, description, examples
        info_group = QGroupBox("Информация о модели")
        info_grid = QGridLayout(info_group)
        info_grid.addWidget(QLabel("Название:"), 0, 0)
        self.name_edit = QLineEdit()
        info_grid.addWidget(self.name_edit, 0, 1)
        info_grid.addWidget(QLabel("Описание:"), 1, 0)
        self.desc_edit = QLineEdit()
        info_grid.addWidget(self.desc_edit, 1, 1)

        info_grid.addWidget(QLabel("Пример:"), 0, 2)
        from PyQt6.QtWidgets import QComboBox
        self.example_combo = QComboBox()
        self.example_combo.addItems(list(EXAMPLES.keys()))
        self.example_combo.currentTextChanged.connect(
            lambda k: self._load_example(EXAMPLES[k])
        )
        info_grid.addWidget(self.example_combo, 0, 3)
        root.addWidget(info_group)

        # Variables
        vars_group = QGroupBox("Переменные состояния (через запятую)")
        vars_layout = QHBoxLayout(vars_group)
        vars_layout.addWidget(QLabel("Переменные:"))
        self.vars_edit = QLineEdit()
        vars_layout.addWidget(self.vars_edit)
        root.addWidget(vars_group)

        # Equations
        eq_group = QGroupBox(
            "Правые части ODE (по одной на строку; порядок соответствует переменным)"
        )
        eq_layout = QVBoxLayout(eq_group)
        mono = QFont("Consolas", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self.equations_edit = QTextEdit()
        self.equations_edit.setFont(mono)
        self.equations_edit.setMaximumHeight(110)
        eq_layout.addWidget(self.equations_edit)
        eq_layout.addWidget(
            QLabel("Доступно: t, все переменные, все параметры, sin, cos, exp, sqrt, log, pi, e, np")
        )
        root.addWidget(eq_group)

        # Parameters table
        params_group = QGroupBox("Параметры модели")
        params_layout = QVBoxLayout(params_group)
        add_btn = QPushButton("+ Добавить параметр")
        add_btn.setFixedWidth(160)
        add_btn.clicked.connect(self._add_param_row)
        params_layout.addWidget(add_btn)
        self.params_table = QTableWidget(0, 5)
        self.params_table.setHorizontalHeaderLabels(
            ["Имя", "Отображение", "Значение", "Мин", "Макс"]
        )
        self.params_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.params_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.params_table.setFixedHeight(130)

        del_btn = QPushButton("Удалить строку")
        del_btn.setFixedWidth(120)
        del_btn.clicked.connect(self._del_param_row)
        params_layout.addWidget(self.params_table)
        params_layout.addWidget(del_btn)
        root.addWidget(params_group)

        # Initial conditions
        ic_group = QGroupBox("Начальные условия (формат: x = 1.0)")
        ic_layout = QVBoxLayout(ic_group)
        self.ic_edit = QTextEdit()
        self.ic_edit.setFont(mono)
        self.ic_edit.setMaximumHeight(80)
        ic_layout.addWidget(self.ic_edit)
        root.addWidget(ic_group)

        # Buttons
        btn_row = QHBoxLayout()
        test_btn = QPushButton("Проверить")
        test_btn.clicked.connect(self._test_model)
        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        ok_btn = QPushButton("Создать модель")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; padding: 8px 18px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        ok_btn.clicked.connect(self._create_model)
        btn_row.addWidget(ok_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    def _load_example(self, data: dict):
        self.name_edit.setText(data["name"])
        self.desc_edit.setText(data["description"])
        self.vars_edit.setText(data["state_vars"])
        self.equations_edit.setPlainText(data["equations"])
        self.ic_edit.setPlainText(data["initial_conds"])

        self.params_table.setRowCount(0)
        for row_data in data["params"]:
            self._add_param_row(row_data)

    def _add_param_row(self, data: tuple | None = None):
        defaults = ("param", "Параметр", "1.0", "0.0", "10.0")
        values = data if data else defaults
        row = self.params_table.rowCount()
        self.params_table.insertRow(row)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.params_table.setItem(row, col, item)

    def _del_param_row(self):
        rows = {idx.row() for idx in self.params_table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            self.params_table.removeRow(row)

    # ------------------------------------------------------------------
    def _parse_model(self) -> CustomModel:
        name = self.name_edit.text().strip() or "Пользовательская модель"
        description = self.desc_edit.text().strip()

        state_names = [v.strip() for v in self.vars_edit.text().split(',') if v.strip()]
        if not state_names:
            raise ValueError("Введите хотя бы одну переменную состояния.")

        equations = [
            line.strip()
            for line in self.equations_edit.toPlainText().splitlines()
            if line.strip()
        ]
        if len(equations) != len(state_names):
            raise ValueError(
                f"Уравнений: {len(equations)}, переменных: {len(state_names)}. "
                "Должно быть поровну."
            )

        parameters: list[Parameter] = []
        for row in range(self.params_table.rowCount()):
            try:
                p_name = self.params_table.item(row, 0).text().strip()
                p_display = self.params_table.item(row, 1).text().strip()
                p_default = float(self.params_table.item(row, 2).text())
                p_min = float(self.params_table.item(row, 3).text())
                p_max = float(self.params_table.item(row, 4).text())
            except (AttributeError, ValueError) as exc:
                raise ValueError(f"Ошибка в строке параметра {row + 1}: {exc}") from exc
            parameters.append(Parameter(
                name=p_name,
                display_name=p_display,
                default_value=p_default,
                min_value=p_min,
                max_value=p_max,
                step=max((p_max - p_min) / 200, 1e-6),
            ))

        initial_conditions: dict[str, float] = {}
        for line in self.ic_edit.toPlainText().splitlines():
            line = line.strip()
            if '=' in line:
                key, _, val = line.partition('=')
                try:
                    initial_conditions[key.strip()] = float(val.strip())
                except ValueError:
                    pass
        for var in state_names:
            initial_conditions.setdefault(var, 0.0)

        return CustomModel(
            name=name,
            description=description,
            state_names=state_names,
            equations=equations,
            parameters=parameters,
            initial_conditions=initial_conditions,
        )

    def _test_model(self):
        try:
            model = self._parse_model()
            params = {p.name: p.default_value for p in model.parameters}
            state = model.get_initial_state(params)
            derivs = model.derivatives(0.0, state, params)
            QMessageBox.information(
                self, "Тест успешен",
                f"Модель «{model.name}» работает!\n\n"
                f"Начальное состояние:\n  {dict(zip(model.state_names, state))}\n\n"
                f"Производные при t=0:\n  {dict(zip(model.state_names, derivs))}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def _create_model(self):
        try:
            self._model = self._parse_model()
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def get_model(self) -> CustomModel | None:
        return self._model
