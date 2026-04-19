from typing import Dict, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QSlider,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..core.interfaces import Parameter


class ParameterEditor(QWidget):
    """Редактор одного параметра — слайдер + спинбокс."""

    value_changed = pyqtSignal(str, float)

    def __init__(self, param: Parameter, parent=None):
        super().__init__(parent)
        self.param = param
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Название
        name_label = QLabel(f"{self.param.display_name}:")
        name_label.setMinimumWidth(160)
        name_label.setToolTip(self.param.description)
        layout.addWidget(name_label)

        # Слайдер
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(self._to_slider(self.param.default_value))
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider, stretch=1)

        # Спинбокс
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(self.param.min_value, self.param.max_value)
        self.spinbox.setSingleStep(self.param.step)
        self.spinbox.setValue(self.param.default_value)
        self.spinbox.setDecimals(self._decimals())
        self.spinbox.setMinimumWidth(90)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        layout.addWidget(self.spinbox)

        # Единица измерения
        if self.param.unit:
            layout.addWidget(QLabel(self.param.unit))

    def _decimals(self) -> int:
        step = self.param.step
        if step >= 1:    return 0
        if step >= 0.1:  return 1
        if step >= 0.01: return 2
        return 3

    def _to_slider(self, value: float) -> int:
        r = self.param.max_value - self.param.min_value
        if r == 0:
            return 500
        return int((value - self.param.min_value) / r * 1000)

    def _to_value(self, slider_val: int) -> float:
        r = self.param.max_value - self.param.min_value
        return self.param.min_value + slider_val / 1000.0 * r

    def _on_slider_changed(self, value: int):
        if self._updating:
            return
        self._updating = True
        new_value = self._to_value(value)
        self.spinbox.setValue(new_value)
        self.value_changed.emit(self.param.name, new_value)
        self._updating = False

    def _on_spinbox_changed(self, value: float):
        if self._updating:
            return
        self._updating = True
        self.slider.setValue(self._to_slider(value))
        self.value_changed.emit(self.param.name, value)
        self._updating = False

    def get_value(self) -> float:
        return self.spinbox.value()

    def set_value(self, value: float):
        self._updating = True
        self.spinbox.setValue(value)
        self.slider.setValue(self._to_slider(value))
        self._updating = False

    def reset(self):
        self.set_value(self.param.default_value)


class ParametersPanel(QWidget):
    """Панель со всеми параметрами модели."""

    parameters_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: Dict[str, ParameterEditor] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Параметры модели")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("padding: 5px; background-color: #2c3e50; color: white;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(4)

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

    def set_parameters(self, parameters: List[Parameter]):
        self._clear()

        for param in parameters:
            editor = ParameterEditor(param)
            editor.value_changed.connect(self._on_changed)
            self._editors[param.name] = editor
            self.content_layout.addWidget(editor)

        self.content_layout.addStretch()

    def _clear(self):
        for editor in self._editors.values():
            editor.deleteLater()
        self._editors.clear()

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_changed(self, name: str, value: float):
        self.parameters_changed.emit(self.get_values())

    def get_values(self) -> Dict[str, float]:
        return {name: editor.get_value() for name, editor in self._editors.items()}

    def reset_all(self):
        for editor in self._editors.values():
            editor.reset()
        self.parameters_changed.emit(self.get_values())