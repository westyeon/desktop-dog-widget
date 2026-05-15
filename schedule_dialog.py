"""
schedule_dialog.py
메뉴바 → '일정 관리' 클릭 시 열리는 다이얼로그.
일정 추가(제목, 시각, 몇 분 전 알림) / 삭제 기능.
"""
import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QScrollArea,
    QWidget, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
import storage


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📅 일정 관리")
        self.setFixedWidth(360)
        self.setStyleSheet("background: white; font-size: 13px;")
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(QLabel("📅 일정 관리", styleSheet="font-size:15px; font-weight:bold;"))

        # ── 입력 영역 ──────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setStyleSheet("background:#f9f9f9; border-radius:10px; padding:8px;")
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(8)

        # 제목
        self.title_input = QLineEdit(placeholderText="일정 제목 (예: 티켓팅)")
        self.title_input.setStyleSheet(self._input_style())
        input_layout.addWidget(self.title_input)

        # 시간 선택 (시 / 분)
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("시각:"))

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setSuffix("시")
        self.hour_spin.setFixedWidth(70)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setSuffix("분")
        self.minute_spin.setSingleStep(5)
        self.minute_spin.setFixedWidth(70)

        time_row.addWidget(self.hour_spin)
        time_row.addWidget(self.minute_spin)
        time_row.addStretch()
        input_layout.addLayout(time_row)

        # 알림 시간 (몇 분 전) — 체크박스로 복수 선택
        notify_row = QHBoxLayout()
        notify_row.addWidget(QLabel("알림:"))
        self.notify_checks = {}
        for mins in [5, 10, 15, 30]:
            cb = QCheckBox(f"{mins}분 전")
            cb.setChecked(mins == 10)  # 기본 10분 전 체크
            self.notify_checks[mins] = cb
            notify_row.addWidget(cb)
        input_layout.addLayout(notify_row)

        # 추가 버튼
        add_btn = QPushButton("+ 일정 추가")
        add_btn.setStyleSheet("""
            QPushButton {
                background:#333; color:white; border-radius:8px;
                padding:8px; font-weight:bold;
            }
            QPushButton:hover { background:#555; }
        """)
        add_btn.clicked.connect(self._add_schedule)
        input_layout.addWidget(add_btn)

        layout.addWidget(input_frame)

        # ── 등록된 일정 목록 ───────────────────────────────────────
        layout.addWidget(QLabel("등록된 일정", styleSheet="font-weight:bold;"))

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(200)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(4)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll)

    def _input_style(self):
        return """
            QLineEdit {
                border:1px solid #ddd; border-radius:8px;
                padding:6px 10px; background:white;
            }
            QLineEdit:focus { border:1px solid #aaa; }
        """

    def _refresh(self):
        """등록된 일정 목록 다시 그리기."""
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        schedules = storage.load_schedules()
        if not schedules:
            empty = QLabel("등록된 일정이 없어요.")
            empty.setStyleSheet("color:#aaa; padding:8px;")
            self.list_layout.insertWidget(0, empty)
            return

        for i, s in enumerate(schedules):
            self._add_row(i, s)

    def _add_row(self, index, s):
        row_w = QWidget()
        row = QHBoxLayout(row_w)
        row.setContentsMargins(4, 2, 4, 2)

        mins_str = ", ".join(f"{m}분 전" for m in s.get("notify_minutes", [10]))
        text = f"🕐 {s['hour']:02d}:{s['minute']:02d}  {s['title']}  ({mins_str})"
        label = QLabel(text)
        label.setStyleSheet("font-size:12px;")

        del_btn = QPushButton("×")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet("""
            QPushButton { background:#ffdddd; color:#cc0000;
                          border-radius:11px; font-weight:bold; border:none; }
            QPushButton:hover { background:#ffbbbb; }
        """)
        del_btn.clicked.connect(lambda _, i=index: self._delete(i))

        row.addWidget(label)
        row.addStretch()
        row.addWidget(del_btn)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row_w)

    def _add_schedule(self):
        title = self.title_input.text().strip()
        if not title:
            return

        notify_minutes = [m for m, cb in self.notify_checks.items() if cb.isChecked()]
        if not notify_minutes:
            notify_minutes = [10]

        schedule = {
            "id": str(uuid.uuid4()),
            "title": title,
            "hour": self.hour_spin.value(),
            "minute": self.minute_spin.value(),
            "notify_minutes": sorted(notify_minutes),
        }

        schedules = storage.load_schedules()
        schedules.append(schedule)
        storage.save_schedules(schedules)
        self.title_input.clear()
        self._refresh()

    def _delete(self, index):
        schedules = storage.load_schedules()
        schedules.pop(index)
        storage.save_schedules(schedules)
        self._refresh()