import re
import traceback
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QTextEdit, QLabel, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
)

from ..core.interfaces import SimulationResult


_SAFE_BUILTINS = {
    'abs': abs, 'round': round, 'min': min, 'max': max,
    'len': len, 'range': range, 'enumerate': enumerate,
    'zip': zip, 'list': list, 'dict': dict, 'tuple': tuple,
    'str': str, 'int': int, 'float': float, 'bool': bool,
    'print': None,  # replaced in exec namespace
    '__builtins__': {},
}

SCRIPT_TEMPLATE = """\
# Скрипт-редактор — доступны: np, result, scipy.signal
# 'result' — последний результат симуляции

if result is not None:
    t = result.time
    states = result.states

    for var_name, values in states.items():
        print(f"=== {var_name} ===")
        print(f"  Мин:      {values.min():.6g}")
        print(f"  Макс:     {values.max():.6g}")
        print(f"  Среднее:  {values.mean():.6g}")
        print(f"  Ст.откл.: {values.std():.6g}")

    # Пример: поиск пиков первой переменной
    from scipy.signal import find_peaks
    first_var = list(states.values())[0]
    peaks, _ = find_peaks(first_var, height=first_var.mean())
    if len(peaks) >= 2:
        period = np.mean(np.diff(t[peaks]))
        print(f"\\nПериод колебаний: {period:.4f}")
        print(f"Частота: {1/period:.4f} Гц")
    else:
        print("\\nПики не обнаружены.")
else:
    print("Нет данных. Запустите симуляцию.")
"""


class _PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument):
        super().__init__(document)

        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#569cd6"))
        kw_fmt.setFontWeight(700)
        keywords = [
            'import', 'from', 'def', 'class', 'return', 'if', 'else', 'elif',
            'for', 'while', 'in', 'not', 'and', 'or', 'True', 'False', 'None',
            'lambda', 'with', 'as', 'try', 'except', 'finally', 'pass', 'break',
            'continue', 'print', 'range', 'len', 'list', 'dict', 'str', 'int', 'float',
        ]
        kw_patterns = [rf'\b{kw}\b' for kw in keywords]

        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#ce9178"))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#6a9955"))

        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#b5cea8"))

        func_fmt = QTextCharFormat()
        func_fmt.setForeground(QColor("#dcdcaa"))

        self._rules = (
            [(re.compile(p), kw_fmt) for p in kw_patterns]
            + [(re.compile(r'#[^\n]*'), comment_fmt)]
            + [(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), str_fmt)]
            + [(re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'"), str_fmt)]
            + [(re.compile(r'\b\d+\.?\d*(?:[eE][+-]?\d+)?\b'), num_fmt)]
            + [(re.compile(r'\b([A-Za-z_]\w*)\s*(?=\()'), func_fmt)]
        )

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


class ScriptEditor(QWidget):
    """Python-редактор скриптов для анализа результатов симуляции."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: SimulationResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        toolbar = QHBoxLayout()
        run_btn = QPushButton("▶ Выполнить (F9)")
        run_btn.setShortcut("F9")
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; padding: 6px 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        run_btn.clicked.connect(self._execute)
        toolbar.addWidget(run_btn)

        clear_output_btn = QPushButton("Очистить вывод")
        clear_output_btn.setStyleSheet("padding: 6px 10px; border-radius: 4px;")
        clear_output_btn.clicked.connect(lambda: self.output.clear())
        toolbar.addWidget(clear_output_btn)

        template_btn = QPushButton("Шаблон")
        template_btn.setStyleSheet("padding: 6px 10px; border-radius: 4px;")
        template_btn.clicked.connect(self._load_template)
        toolbar.addWidget(template_btn)

        toolbar.addStretch()
        hint = QLabel("numpy → 'np'  |  результат → 'result'  |  F9 — выполнить")
        hint.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        toolbar.addWidget(hint)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        mono = QFont("Consolas", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)

        self.editor = QPlainTextEdit()
        self.editor.setFont(mono)
        self.editor.setPlainText(SCRIPT_TEMPLATE)
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 4px;
            }
        """)
        self.editor.setTabStopDistance(28)
        _PythonHighlighter(self.editor.document())
        splitter.addWidget(self.editor)

        out_widget = QWidget()
        out_layout = QVBoxLayout(out_widget)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.addWidget(QLabel("Вывод:"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(mono)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: #00dd00;
                border: none;
                padding: 4px;
            }
        """)
        out_layout.addWidget(self.output)
        splitter.addWidget(out_widget)

        splitter.setSizes([280, 140])
        layout.addWidget(splitter)

    def set_result(self, result: SimulationResult | None):
        self._result = result

    def _load_template(self):
        self.editor.setPlainText(SCRIPT_TEMPLATE)

    def _execute(self):
        code = self.editor.toPlainText()
        self.output.clear()

        captured: list[str] = []

        def _print(*args, **kwargs):
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            text = sep.join(str(a) for a in args) + end
            captured.append(text)

        namespace: dict = {
            'np': np,
            'result': self._result,
            'print': _print,
        }
        try:
            from scipy.signal import find_peaks
            namespace['find_peaks'] = find_peaks
            from scipy import signal as _signal
            namespace['scipy_signal'] = _signal
        except ImportError:
            pass

        try:
            exec(compile(code, '<script>', 'exec'), namespace)  # noqa: S102
            for line in captured:
                self.output.insertPlainText(line)
        except Exception:
            self.output.setTextColor(QColor("#ff5555"))
            self.output.append("=== ОШИБКА ===")
            self.output.append(traceback.format_exc())
            self.output.setTextColor(QColor("#00dd00"))
        else:
            if not captured:
                self.output.setTextColor(QColor("#888"))
                self.output.append("(нет вывода)")
                self.output.setTextColor(QColor("#00dd00"))
