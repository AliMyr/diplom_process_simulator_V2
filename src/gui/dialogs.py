# src/gui/dialogs.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.utils.presets import PresetManager, SimulationPreset


class SavePresetDialog(QDialog):
    """Диалог для сохранения preset-а."""

    def __init__(self, model_name: str, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.preset = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Сохранить preset")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Название preset-а
        layout.addWidget(QLabel("Название preset-а:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("например: oscillator_damped_test")
        layout.addWidget(self.name_input)

        # Описание
        layout.addWidget(QLabel("Описание (опционально):"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)

        # Кнопки
        buttons = QHBoxLayout()

        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("✕ Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def get_preset(self) -> SimulationPreset:
        """Получить заполненный preset."""
        return self.preset

    def accept(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название preset-а!")
            return

        # Убрать пробелы и спецсимволы
        name = name.replace(" ", "_").replace("/", "_")

        self.preset = SimulationPreset(
            name=name,
            model_name=self.model_name,
            parameters={},  # Заполняется снаружи
            simulation_settings={},
            description=self.description_input.toPlainText()
        )

        super().accept()


class LoadPresetDialog(QDialog):
    """Диалог для загрузки preset-а."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = PresetManager()
        self.selected_preset = None
        self._setup_ui()
        self._load_presets_list()

    def _setup_ui(self):
        self.setWindowTitle("Загрузить preset")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)

        # Список preset-ов
        layout.addWidget(QLabel("Доступные preset-ы:"))
        self.presets_list = QListWidget()
        self.presets_list.itemSelectionChanged.connect(self._on_preset_selected)
        layout.addWidget(self.presets_list)

        # Информация о выбранном
        layout.addWidget(QLabel("Информация:"))
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(self.info_text)

        # Кнопки
        buttons = QHBoxLayout()

        load_btn = QPushButton("📂 Загрузить")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #5dade2; }
        """)
        load_btn.clicked.connect(self.accept)
        buttons.addWidget(load_btn)

        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #ec7063; }
        """)
        delete_btn.clicked.connect(self._delete_preset)
        buttons.addWidget(delete_btn)

        cancel_btn = QPushButton("✕ Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def _load_presets_list(self):
        """Загрузить список preset-ов."""
        self.presets_list.clear()
        presets = self.manager.list_presets()

        if not presets:
            self.info_text.setText("Нет сохранённых preset-ов")
            return

        for name in presets:
            self.presets_list.addItem(name)

    def _on_preset_selected(self):
        """Обновить информацию о выбранном preset-е."""
        item = self.presets_list.currentItem()
        if item:
            name = item.text()
            info = self.manager.get_preset_info(name)
            if info:
                text = f"📋 {info['name']}\n"
                text += f"🔬 Модель: {info['model']}\n"
                text += f"📅 Создан: {info['created']}\n"
                text += f"📝 Описание: {info['description']}"
                self.info_text.setText(text)
                self.selected_preset = name

    def _delete_preset(self):
        """Удалить выбранный preset."""
        if not self.selected_preset:
            QMessageBox.warning(self, "Ошибка", "Выберите preset для удаления!")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить preset '{self.selected_preset}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.delete_preset(self.selected_preset):
                QMessageBox.information(self, "Успех", "Preset удалён!")
                self._load_presets_list()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить preset!")

    def get_preset_name(self) -> str:
        """Получить имя выбранного preset-а."""
        return self.selected_preset


class ModelInfoDialog(QDialog):
    """Диалог с информацией о модели (формулы, параметры, etc)."""

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"О модели: {self.model.name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # Название
        title = QLabel(self.model.name)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # Описание
        layout.addWidget(QLabel("📝 Описание:"))
        desc_text = QTextEdit()
        desc_text.setPlainText(self.model.description)
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(80)
        layout.addWidget(desc_text)

        # Переменные состояния
        layout.addWidget(QLabel("🔤 Переменные состояния:"))
        states_text = QTextEdit()
        states_text.setPlainText(", ".join(self.model.state_names))
        states_text.setReadOnly(True)
        states_text.setMaximumHeight(40)
        layout.addWidget(states_text)

        # Параметры
        layout.addWidget(QLabel("⚙️ Параметры:"))
        params_text = QTextEdit()

        params_info = []
        for param in self.model.parameters:
            info = f"• {param.display_name} ({param.name}): "
            info += f"[{param.min_value}, {param.max_value}]"
            if param.unit:
                info += f" {param.unit}"
            if param.description:
                info += f"\n  {param.description}"
            params_info.append(info)

        params_text.setPlainText("\n\n".join(params_info))
        params_text.setReadOnly(True)
        layout.addWidget(params_text, stretch=1)

        # Кнопка закрытия
        close_btn = QPushButton("✕ Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)