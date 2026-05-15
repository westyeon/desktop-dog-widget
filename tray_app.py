import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal
import storage


class TrayApp(QObject):
    movement_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        config = storage.load_config()
        self.is_moving = config.get("moving", True)
        self._dialog = None  # 일정 다이얼로그 참조 보관
        self._build()

    def _build(self):
        icon_path = os.path.join(
            os.path.dirname(__file__), "assets", "walk_right", "frame_00.png"
        )
        self.tray = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray.setToolTip("🐾 Desktop Dog")

        menu = QMenu()

        # ── 이동 모드 ─────────────────────────────────────────
        header = menu.addAction("🐾 이동 모드")
        header.setEnabled(False)
        menu.addSeparator()

        self.act_move = menu.addAction("돌아다니기")
        self.act_move.setCheckable(True)
        self.act_move.setChecked(self.is_moving)

        self.act_still = menu.addAction("가만히 있기")
        self.act_still.setCheckable(True)
        self.act_still.setChecked(not self.is_moving)

        self.act_move.triggered.connect(lambda: self._set_mode(True))
        self.act_still.triggered.connect(lambda: self._set_mode(False))

        # ── 일정 관리 ─────────────────────────────────────────
        menu.addSeparator()
        schedule_action = menu.addAction("📅 일정 관리")
        schedule_action.triggered.connect(self._open_schedule)

        menu.addSeparator()
        menu.addAction("종료").triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def _set_mode(self, moving: bool):
        self.is_moving = moving
        self.act_move.setChecked(moving)
        self.act_still.setChecked(not moving)
        self.movement_changed.emit(moving)
        storage.save_config({"moving": moving})

    def _open_schedule(self):
        """일정 관리 다이얼로그 열기. 이미 열려있으면 앞으로."""
        from schedule_dialog import ScheduleDialog
        if self._dialog is None or not self._dialog.isVisible():
            self._dialog = ScheduleDialog()
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()