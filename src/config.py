# src/config.py

from pathlib import Path

# Директории
APP_DIR = Path(__file__).parent.parent
DATA_DIR = Path.home() / ".diplom_simulator"
PRESETS_DIR = DATA_DIR / "presets"
LOGS_DIR = DATA_DIR / "logs"

# Версия
APP_VERSION = "0.1.0"
APP_NAME = "Симулятор процессов"

# Стили
THEME_COLORS = {
    "primary": "#3498db",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "dark": "#2c3e50",
    "light": "#ecf0f1",
}

# Настройки GUI
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_LEFT_PANEL_WIDTH = 420

# Настройки симуляции
DEFAULT_T_START = 0.0
DEFAULT_T_END = 10.0
DEFAULT_NUM_POINTS = 1000
MAX_NUM_POINTS = 100000

# Солвер
SOLVER_METHOD = 'RK45'
SOLVER_RTOL = 1e-6
SOLVER_ATOL = 1e-9

# Логирование
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'