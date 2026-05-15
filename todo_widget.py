from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPainterPath
import storage


class TodoWidget(QWidget):
    # 할일 목록이 변경될 때마다 emit → pet_widget이 받아서 말풍선 업데이트
    todos_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self._build_ui()
        self._load()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 14)

        self.card = QFrame(self)
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background: white;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
        """)
        outer.addWidget(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)

        title = QLabel("🐾 할 일 목록")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#333;")
        card_layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#f0f0f0;")
        card_layout.addWidget(line)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setFixedHeight(200)
        self.scroll.setStyleSheet("background:transparent;")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(4)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_container)
        card_layout.addWidget(self.scroll)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("할 일을 입력하세요...")
        self.input_field.setStyleSheet("""
            QLineEdit { border:1px solid #ddd; border-radius:10px;
                        padding:6px 12px; font-size:13px; background:#f9f9f9; }
            QLineEdit:focus { border:1px solid #aaa; background:white; }
        """)
        self.input_field.returnPressed.connect(self._add_todo)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(32, 32)
        add_btn.setStyleSheet("""
            QPushButton { background:#333; color:white; border-radius:16px;
                          font-size:20px; font-weight:bold; }
            QPushButton:hover { background:#555; }
        """)
        add_btn.clicked.connect(self._add_todo)

        input_row.addWidget(self.input_field)
        input_row.addWidget(add_btn)
        card_layout.addLayout(input_row)

        close_btn = QPushButton("닫기")
        close_btn.setStyleSheet("""
            QPushButton { background:#f0f0f0; color:#555; border-radius:8px;
                          padding:5px; font-size:12px; border:none; }
            QPushButton:hover { background:#ddd; }
        """)
        close_btn.clicked.connect(self.hide)
        card_layout.addWidget(close_btn)

        self.setFixedWidth(280)

    def _load(self):
        self.todos = storage.load_todos()
        self._refresh()

    def _refresh(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.todos:
            empty = QLabel("아직 할 일이 없어요 😴")
            empty.setStyleSheet("color:#aaa; font-size:12px; padding:8px;")
            self.list_layout.insertWidget(0, empty)
            return

        for i, todo in enumerate(reversed(self.todos)):
            real_index = len(self.todos) - 1 - i
            self._add_row(real_index, todo)

    def _add_row(self, index, todo):
        row_widget = QWidget()
        row_widget.setStyleSheet("background:transparent;")
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 2, 0, 2)

        cb = QCheckBox(todo["text"])
        cb.setChecked(todo["done"])
        if todo["done"]:
            cb.setStyleSheet(
                "QCheckBox { font-size:13px; color:#bbb; text-decoration:line-through; }"
            )
        else:
            cb.setStyleSheet("QCheckBox { font-size:13px; color:#333; }")

        cb.stateChanged.connect(lambda state, i=index: self._toggle(i, state))

        del_btn = QPushButton("×")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet("""
            QPushButton { background:#ffdddd; color:#cc0000;
                          border-radius:11px; font-size:13px;
                          font-weight:bold; border:none; }
            QPushButton:hover { background:#ffbbbb; }
        """)
        del_btn.clicked.connect(lambda _, i=index: self._delete(i))

        row.addWidget(cb)
        row.addStretch()
        row.addWidget(del_btn)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row_widget)

    def _add_todo(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.todos.append({"text": text, "done": False})
        storage.save_todos(self.todos)
        self.input_field.clear()
        self._refresh()
        self.todos_changed.emit()  # ← 변경 신호

    def _toggle(self, index, state):
        self.todos[index]["done"] = bool(state)
        storage.save_todos(self.todos)
        self._refresh()
        self.todos_changed.emit()  # ← 변경 신호

    def _delete(self, index):
        self.todos.pop(index)
        storage.save_todos(self.todos)
        self._refresh()
        self.todos_changed.emit()  # ← 변경 신호

    def get_top_todo(self):
        """
        미완료 할일 중 가장 최근 항목 텍스트 반환.
        없으면 None.
        """
        undone = [t for t in reversed(self.todos) if not t["done"]]
        return undone[0]["text"] if undone else None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        mid = w // 2
        painter.setBrush(QColor("white"))
        painter.setPen(QColor("#e0e0e0"))
        path = QPainterPath()
        path.moveTo(mid - 10, h - 14)
        path.lineTo(mid, h)
        path.lineTo(mid + 10, h - 14)
        path.closeSubpath()
        painter.drawPath(path)

    def show_near(self, dog_x, dog_y, dog_w, dog_h):
        self.adjustSize()
        popup_w = self.width()
        popup_h = self.sizeHint().height()
        x = dog_x + dog_w // 2 - popup_w // 2
        y = dog_y - popup_h - 8

        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            if y < geo.y():
                y = dog_y + dog_h + 8
            x = max(geo.x(), min(x, geo.x() + geo.width() - popup_w))

        self.move(x, y)
        self.show()
        self.activateWindow()
        self.input_field.setFocus()

    def update_position(self, dog_x, dog_y, dog_w, dog_h):
        x = dog_x + dog_w // 2 - self.width() // 2
        y = dog_y - self.height() - 8
        self.move(x, y)