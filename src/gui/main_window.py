from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QMessageBox,
    QFileDialog, QComboBox, QLabel, QPushButton,
    QTabWidget, QTextEdit, QGroupBox, QApplication,
    QDoubleSpinBox, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont

from ..core.simulation_engine import SimulationEngine
from ..core.interfaces import SimulationResult
from ..models import get_models_by_category
from ..utils.export import ExporterFactory
from ..utils.presets import PresetManager, SimulationPreset
from ..utils.logger import setup_logger

from .parameters_panel import ParametersPanel
from .visualization_canvas import VisualizationWidget
from .dialogs import SavePresetDialog, LoadPresetDialog, ModelInfoDialog


class ModelSelectorWidget(QWidget):
    """Виджет выбора модели по категориям."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._models_by_category = get_models_by_category()
        self._current_model = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Выбор модели")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("padding: 5px; background-color: #2c3e50; color: white;")
        layout.addWidget(header)

        # Категория
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(self._models_by_category.keys()))
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        cat_layout.addWidget(self.category_combo, stretch=1)
        layout.addLayout(cat_layout)

        # Модель
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Модель:"))
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo, stretch=1)
        layout.addLayout(model_layout)

        # Описание
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        self.description_text.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #dee2e6;"
        )
        layout.addWidget(self.description_text)

        self._on_category_changed(self.category_combo.currentText())

    def _on_category_changed(self, category: str):
        self.model_combo.clear()
        if category in self._models_by_category:
            for model in self._models_by_category[category]:
                self.model_combo.addItem(model.name, model)

    def _on_model_changed(self, index: int):
        if index >= 0:
            self._current_model = self.model_combo.itemData(index)
            if self._current_model:
                self.description_text.setText(self._current_model.description)

    def get_current_model(self):
        return self._current_model


class SimulationSettingsPanel(QWidget):
    """Панель настроек времени симуляции."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Настройки симуляции")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("padding: 5px; background-color: #2c3e50; color: white;")
        layout.addWidget(header)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setContentsMargins(10, 10, 10, 10)

        grid.addWidget(QLabel("Начальное время:"), 0, 0)
        self.t_start_spin = QDoubleSpinBox()
        self.t_start_spin.setRange(0, 10000)
        self.t_start_spin.setValue(0)
        self.t_start_spin.setDecimals(2)
        grid.addWidget(self.t_start_spin, 0, 1)

        grid.addWidget(QLabel("Конечное время:"), 1, 0)
        self.t_end_spin = QDoubleSpinBox()
        self.t_end_spin.setRange(0.1, 100000)
        self.t_end_spin.setValue(10)
        self.t_end_spin.setDecimals(2)
        grid.addWidget(self.t_end_spin, 1, 1)

        grid.addWidget(QLabel("Количество точек:"), 2, 0)
        self.num_points_spin = QDoubleSpinBox()
        self.num_points_spin.setRange(10, 100000)
        self.num_points_spin.setValue(1000)
        self.num_points_spin.setDecimals(0)
        grid.addWidget(self.num_points_spin, 2, 1)

        layout.addWidget(content)

    def get_settings(self) -> dict:
        return {
            't_start': self.t_start_spin.value(),
            't_end': self.t_end_spin.value(),
            'num_points': int(self.num_points_spin.value())
        }

    def set_settings(self, settings: dict):
        if 't_start' in settings:
            self.t_start_spin.setValue(settings['t_start'])
        if 't_end' in settings:
            self.t_end_spin.setValue(settings['t_end'])
        if 'num_points' in settings:
            self.num_points_spin.setValue(settings['num_points'])


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()

        self.engine = SimulationEngine()
        self.current_result: Optional[SimulationResult] = None
        self.preset_manager = PresetManager()
        self.logger = setup_logger("SimulationUI")

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        self._on_model_selected()

    def _setup_ui(self):
        self.setWindowTitle("Симулятор процессов")
        self.setMinimumSize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === Левая панель ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.model_selector = ModelSelectorWidget()
        left_layout.addWidget(self.model_selector)

        self.params_panel = ParametersPanel()
        left_layout.addWidget(self.params_panel, stretch=1)

        self.sim_settings = SimulationSettingsPanel()
        left_layout.addWidget(self.sim_settings)

        # Кнопки
        buttons_group = QGroupBox("Управление")
        buttons_layout = QHBoxLayout(buttons_group)

        self.run_btn = QPushButton("▶ Запустить")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        buttons_layout.addWidget(self.run_btn)

        self.reset_btn = QPushButton("⟲ Сброс")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        buttons_layout.addWidget(self.reset_btn)

        left_layout.addWidget(buttons_group)
        left_panel.setMaximumWidth(420)
        splitter.addWidget(left_panel)

        # === Правая панель ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.plot_tabs = QTabWidget()

        self.time_plot = VisualizationWidget()
        self.plot_tabs.addTab(self.time_plot, "Временные ряды")

        self.phase_plot = VisualizationWidget()
        self.plot_tabs.addTab(self.phase_plot, "Фазовый портрет")

        right_layout.addWidget(self.plot_tabs)

        # Инфо панель
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout(info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(80)
        info_layout.addWidget(self.info_text)
        right_layout.addWidget(info_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 820])
        main_layout.addWidget(splitter)

    def _setup_menu(self):
        menubar = self.menuBar()

        # === Файл ===
        file_menu = menubar.addMenu("Файл")

        save_preset_action = QAction("💾 Сохранить preset", self)
        save_preset_action.triggered.connect(self._save_preset)
        file_menu.addAction(save_preset_action)

        load_preset_action = QAction("📂 Загрузить preset", self)
        load_preset_action.triggered.connect(self._load_preset)
        file_menu.addAction(load_preset_action)

        file_menu.addSeparator()

        export_action = QAction("📊 Экспорт данных", self)
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)

        save_plot_action = QAction("🖼️ Сохранить график", self)
        save_plot_action.triggered.connect(self._save_plot)
        file_menu.addAction(save_plot_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # === Симуляция ===
        sim_menu = menubar.addMenu("Симуляция")

        run_action = QAction("▶️ Запустить", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._run_simulation)
        sim_menu.addAction(run_action)

        reset_action = QAction("⟲ Сбросить параметры", self)
        reset_action.triggered.connect(self._reset_parameters)
        sim_menu.addAction(reset_action)

        # === Справка ===
        help_menu = menubar.addMenu("Справка")

        model_info_action = QAction("ℹ️ О модели", self)
        model_info_action.triggered.connect(self._show_model_info)
        help_menu.addAction(model_info_action)

    def _setup_toolbar(self):
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        run_action = QAction("▶ Запустить", self)
        run_action.setToolTip("Запустить симуляцию (F5)")
        run_action.triggered.connect(self._run_simulation)
        toolbar.addAction(run_action)

        toolbar.addSeparator()

        export_action = QAction("💾 Экспорт", self)
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)

        save_plot_action = QAction("🖼 Сохранить график", self)
        save_plot_action.triggered.connect(self._save_plot)
        toolbar.addAction(save_plot_action)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готово. Выберите модель и нажмите 'Запустить'")

    def _connect_signals(self):
        self.model_selector.model_combo.currentIndexChanged.connect(self._on_model_selected)
        self.run_btn.clicked.connect(self._run_simulation)
        self.reset_btn.clicked.connect(self._reset_parameters)

    def _on_model_selected(self):
        model = self.model_selector.get_current_model()
        if model:
            self.engine.set_model(model)
            self.params_panel.set_parameters(model.parameters)

            # Подстройка времени под модель
            if "Баллист" in model.name:
                self.sim_settings.set_settings({'t_end': 5, 'num_points': 500})
            elif "SIR" in model.name or "эпидем" in model.name.lower():
                self.sim_settings.set_settings({'t_end': 100, 'num_points': 1000})
            elif "Брюссел" in model.name:
                self.sim_settings.set_settings({'t_end': 30, 'num_points': 1000})
            else:
                self.sim_settings.set_settings({'t_end': 10, 'num_points': 1000})

            self.statusbar.showMessage(f"Выбрана модель: {model.name}")

    def _save_preset(self):
        """Сохранить текущие параметры как preset."""
        model = self.model_selector.get_current_model()
        if not model:
            QMessageBox.warning(self, "Ошибка", "Выберите модель!")
            return

        dialog = SavePresetDialog(model.name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            preset = dialog.get_preset()
            preset.parameters = self.params_panel.get_values()
            preset.simulation_settings = self.sim_settings.get_settings()

            if self.preset_manager.save_preset(preset):
                QMessageBox.information(
                    self, "Успех",
                    f"Preset '{preset.name}' сохранён!"
                )
                self.logger.info(f"Preset saved: {preset.name}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить preset!")

    def _load_preset(self):
        """Загрузить параметры из preset-а."""
        dialog = LoadPresetDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            preset_name = dialog.get_preset_name()
            if preset_name:
                preset = self.preset_manager.load_preset(preset_name)
                if preset:
                    # Найти модель по имени
                    model = None
                    for cat_models in self.model_selector._models_by_category.values():
                        for m in cat_models:
                            if m.name == preset.model_name:
                                model = m
                                break

                    if model:
                        # Установить модель
                        self.model_selector._current_model = model
                        self.engine.set_model(model)
                        self.params_panel.set_parameters(model.parameters)

                        # Установить параметры
                        for name, value in preset.parameters.items():
                            if name in self.params_panel._editors:
                                self.params_panel._editors[name].set_value(value)

                        # Установить настройки времени
                        self.sim_settings.set_settings(preset.simulation_settings)

                        self.statusbar.showMessage(f"Preset '{preset_name}' загружен!")
                        self.logger.info(f"Preset loaded: {preset_name}")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Модель для этого preset-а не найдена!")

    def _show_model_info(self):
        """Показать информацию о текущей модели."""
        model = self.model_selector.get_current_model()
        if not model:
            QMessageBox.warning(self, "Ошибка", "Выберите модель!")
            return

        dialog = ModelInfoDialog(model, self)
        dialog.exec()

    def _run_simulation(self):
        model = self.model_selector.get_current_model()
        if not model:
            QMessageBox.warning(self, "Ошибка", "Выберите модель!")
            return

        try:
            params = self.params_panel.get_values()
            settings = self.sim_settings.get_settings()

            self.engine.set_parameters(params)

            self.statusbar.showMessage("Выполняется симуляци��...")
            QApplication.processEvents()

            result = self.engine.run(
                t_start=settings['t_start'],
                t_end=settings['t_end'],
                num_points=int(settings['num_points'])
            )

            self.current_result = result
            self._update_plots(result, model)
            self._update_info(result, model)

            self.statusbar.showMessage("Симуляция завершена успешно!")
            self.logger.info(f"Simulation completed: {model.name}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка симуляции", str(e))
            self.statusbar.showMessage(f"Ошибка: {str(e)}")
            self.logger.error(f"Simulation error: {str(e)}")

    def _update_plots(self, result: SimulationResult, model):
        config = model.get_plot_config()
        state_names = list(result.states.keys())
        traj_vars = getattr(model, 'trajectory_vars', None)

        if traj_vars and all(v in state_names for v in traj_vars):
            # Баллистика — траектория x vs y
            self.time_plot.plot_result(
                result, config,
                y_vars=[s for s in state_names if s != 'x']
            )
            self.phase_plot.canvas.plot_phase_portrait(
                result, traj_vars[0], traj_vars[1],
                title="Траектория движения"
            )
            self.plot_tabs.setTabText(1, "Траектория")

        elif len(state_names) >= 2:
            # Модели с 2+ переменными — фазовый портрет
            self.time_plot.plot_result(result, config)
            self.phase_plot.canvas.plot_phase_portrait(
                result, state_names[0], state_names[1],
                title=f"Фазовый портрет: {state_names[0]} vs {state_names[1]}"
            )
            self.plot_tabs.setTabText(1, "Фазовый портрет")
            self.plot_tabs.setTabEnabled(1, True)

        else:
            # Модели с одной переменной — только временной ряд
            self.time_plot.plot_result(result, config)
            self.phase_plot.clear()
            self.plot_tabs.setTabText(1, "Фазовый портрет")
            self.plot_tabs.setTabEnabled(1, False)

    def _update_info(self, result: SimulationResult, model=None):
        lines = []
        lines.append(f"Модель: {result.metadata.get('model', 'N/A')}")
        lines.append(f"Время: {result.time[0]:.2f} — {result.time[-1]:.2f}")
        lines.append(f"Точек: {len(result.time)}")

        # Какие переменные показывать
        traj_vars = getattr(model, 'trajectory_vars', None)
        if traj_vars:
            show_vars = traj_vars
        else:
            show_vars = list(result.states.keys())

        lines.append("Статистика:")
        for name in show_vars:
            values = result.states[name]
            lines.append(f"  {name}: min={values.min():.4g}, max={values.max():.4g}")

        self.info_text.setText('\n'.join(lines))

    def _reset_parameters(self):
        self.params_panel.reset_all()
        self.statusbar.showMessage("Параметры сброшены")

    def _export_data(self):
        if not self.current_result:
            QMessageBox.warning(self, "Нет данных", "Сначала выполните симуляцию!")
            return

        formats = ExporterFactory.get_format_descriptions()
        filter_str = ";;".join([f"{desc} (*.{fmt})" for fmt, desc in formats.items()])

        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт данных", "", filter_str
        )

        if filepath:
            for fmt, desc in formats.items():
                if desc in selected_filter:
                    exporter = ExporterFactory.create(fmt)
                    if exporter.export(self.current_result, filepath):
                        self.statusbar.showMessage(f"Сохранено: {filepath}")
                        self.logger.info(f"Export saved: {filepath}")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")
                    break

    def _save_plot(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filepath:
            current_tab = self.plot_tabs.currentWidget()
            if hasattr(current_tab, 'save_figure'):
                current_tab.save_figure(filepath)
                self.statusbar.showMessage(f"График сохранён: {filepath}")
                self.logger.info(f"Plot saved: {filepath}")