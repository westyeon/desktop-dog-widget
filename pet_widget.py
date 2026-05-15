import os, glob, random, ctypes
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPainterPath
from todo_widget import TodoWidget
import storage

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
PET_SIZE  = 100
SPEED     = 2
TICK_MS   = 30
ANIM_MS   = 200

STATE_DURATION = {
    "walk":  (4, 9),
    "stand": (2, 5),
    "sleep": (3, 8),
}
NEXT_STATE = {
    "walk":  ["stand", "walk", "walk"],
    "stand": ["walk", "sleep", "stand"],
    "sleep": ["stand", "stand", "walk"],
}


class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._todo_text   = None
        self._notify_text = None

        self._notify_timer = QTimer(self)
        self._notify_timer.setSingleShot(True)
        self._notify_timer.timeout.connect(self._clear_notify)

    def set_todo(self, text):
        self._todo_text = text
        self._redraw()

    def set_notify(self, msg):
        self._notify_text = msg
        self._notify_timer.start(4000)
        self._redraw()

    def _clear_notify(self):
        self._notify_text = None
        self._redraw()

    def _current_text(self):
        return self._notify_text or self._todo_text

    def _redraw(self):
        text = self._current_text()
        if not text:
            self.hide()
            return
        self.update()
        self.show()

    def update_pos(self, dog_x, dog_y, dog_w):
        if not self._current_text():
            self.hide()
            return
        x = dog_x + dog_w // 2 - self.width() // 2
        y = dog_y - self.height()
        self.move(x, y)
        self.show()

    def paintEvent(self, event):
        text = self._current_text()
        if not text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        fm = painter.fontMetrics()

        text_w = min(fm.horizontalAdvance(text), 200)
        text_h = fm.height()
        pad_x, pad_y = 14, 10
        tail_h = 10

        w = text_w + pad_x * 2
        h = text_h + pad_y * 2 + tail_h
        self.setFixedSize(w, h)

        bubble_h = h - tail_h
        mid = w // 2

        bg     = QColor(255, 255, 255, 240)
        border = QColor(210, 210, 210)

        tail_path = QPainterPath()
        tail_path.moveTo(mid - 9, bubble_h + 1)
        tail_path.lineTo(mid,     h)
        tail_path.lineTo(mid + 9, bubble_h + 1)
        tail_path.closeSubpath()
        painter.setPen(border)
        painter.setBrush(bg)
        painter.drawPath(tail_path)

        painter.setPen(border)
        painter.setBrush(bg)
        painter.drawRoundedRect(0, 0, w, bubble_h, 12, 12)

        painter.setPen(QColor(50, 50, 50))
        painter.drawText(pad_x, pad_y + text_h - 4, text)


class PetWidget(QWidget):
    def __init__(self):
        super().__init__()
        config = storage.load_config()
        self.is_moving = config.get("moving", True)

        self._setup_window()
        self._load_assets()
        self._init_movement()

        if self.is_moving:
            self.state = "walk"
        else:
            self.state = "stand"

        self.frame_index = 0
        self._update_image()

        self._start_timers()

        self.todo   = TodoWidget()
        self.bubble = SpeechBubble()

        self.todo.todos_changed.connect(self._update_bubble)
        self._update_bubble()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            # ← Tool 제거! 이게 비활성화 시 숨기는 원인이었음
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def showEvent(self, event):
        super().showEvent(event)
        self._set_always_on_top()

    def _set_always_on_top(self):
        try:
            from AppKit import (
                NSStatusWindowLevel,
                NSWindowCollectionBehaviorCanJoinAllSpaces
            )
            import objc
            wid = self.winId().__int__()
            ns_view = objc.objc_object(c_void_p=wid)
            ns_window = ns_view.window()
            if ns_window:
                ns_window.setLevel_(NSStatusWindowLevel)
                ns_window.setCollectionBehavior_(
                    NSWindowCollectionBehaviorCanJoinAllSpaces
                )
        except Exception as e:
            print(f"최상단 설정 실패: {e}")

    def _force_on_top(self):
        try:
            from AppKit import NSStatusWindowLevel
            import objc
            wid = self.winId().__int__()
            ns_view = objc.objc_object(c_void_p=wid)
            ns_window = ns_view.window()
            if ns_window:
                ns_window.setLevel_(NSStatusWindowLevel)
                ns_window.orderFrontRegardless()
        except Exception as e:
            print(f"실패: {e}")
            self.raise_()

    def _update_bubble(self):
        text = self.todo.get_top_todo()
        self.bubble.set_todo(text)
        self.bubble.update_pos(self.x(), self.y(), self.width())

    def show_notification(self, msg: str):
        self.bubble.set_notify(msg)
        self.bubble.update_pos(self.x(), self.y(), self.width())

    def _load_assets(self):
        def load_frames(folder):
            paths = sorted(glob.glob(os.path.join(ASSET_DIR, folder, "*.png")))
            return [
                QPixmap(p).scaledToHeight(
                    PET_SIZE, Qt.TransformationMode.SmoothTransformation
                )
                for p in paths
            ] or None

        self.frames = {
            "walk_left":  load_frames("walk_left"),
            "walk_right": load_frames("walk_right"),
            "stand":      load_frames("stand"),
            "sleep":      load_frames("sleep"),
        }

        first = self._get_first_frame()
        self.label = QLabel(self)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.label.setStyleSheet("background: transparent;")
        self.label.setPixmap(first)
        self.label.setFixedSize(first.size())
        self.setFixedSize(first.size())
        self.dx = 1

    def _get_first_frame(self):
        for key in ["walk_right", "walk_left", "stand", "sleep"]:
            if self.frames.get(key):
                return self.frames[key][0]
        raise FileNotFoundError("assets/ 폴더에 이미지가 없습니다!")

    def _current_frames(self):
        if self.state == "walk":
            key = "walk_right" if self.dx == 1 else "walk_left"
        else:
            key = self.state
        frames = self.frames.get(key)
        if not frames:
            for k in ["walk_right", "walk_left", "stand", "sleep"]:
                if self.frames.get(k):
                    return self.frames[k]
        return frames

    def _update_image(self):
        frames = self._current_frames()
        if not frames:
            return
        if self.frame_index >= len(frames):
            self.frame_index = 0
        px = frames[self.frame_index]
        self.label.setPixmap(px)
        if self.label.size() != px.size():
            self.label.setFixedSize(px.size())
            self.setFixedSize(px.size())
        self.label.repaint()

    def _schedule_next_state(self):
        mn, mx = STATE_DURATION[self.state]
        QTimer.singleShot(
            random.randint(mn * 1000, mx * 1000),
            self._transition_state
        )

    def _transition_state(self):
        if not self.is_moving:
            self.state = random.choice(["stand", "sleep"])
        else:
            self.state = random.choice(NEXT_STATE[self.state])
        self.frame_index = 0
        self._update_image()
        self._schedule_next_state()

    def set_moving(self, moving: bool):
        self.is_moving = moving
        if not moving:
            self.state = random.choice(["stand", "sleep"])
            self.frame_index = 0
            self._update_image()

    def _start_timers(self):
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self._on_move_tick)
        self.move_timer.start(TICK_MS)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start(ANIM_MS)

        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self._sync_bubble_pos)
        self.bubble_timer.start(50)

        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self._force_on_top)
        self.top_timer.start(2000)

        self._schedule_next_state()

    def _sync_bubble_pos(self):
        self.bubble.update_pos(self.x(), self.y(), self.width())
        if self.todo.isVisible():
            self.todo.update_position(self.x(), self.y(), self.width(), self.height())

    def _init_movement(self):
        screen = self.screen()
        geo = screen.availableGeometry()
        self.screen_w = geo.width()
        self.screen_h = geo.height()
        self.screen_x = geo.x()
        self.screen_y = geo.y()
        start_x = self.screen_x + self.screen_w // 2 - self.width() // 2
        start_y = self.screen_y + self.screen_h - self.height() - 40
        self.move(start_x, start_y)
        self.dx = 1

    def _on_move_tick(self):
        if not self.is_moving or self.state != "walk":
            return

        x = self.x()
        next_x = x + SPEED * self.dx

        if next_x + self.width() >= self.screen_x + self.screen_w:
            self.dx = -1
            self.frame_index = 0
            self._update_image()
        elif next_x <= self.screen_x:
            self.dx = 1
            self.frame_index = 0
            self._update_image()

        self.move(next_x, self.y())

    def _on_anim_tick(self):
        if self.state != "walk":
            return
        frames = self._current_frames()
        if frames and len(frames) > 1:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self._update_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Clear
        )
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            self._drag_moved  = False
            self.move_timer.stop()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            self._drag_moved = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.move_timer.start(TICK_MS)

        elif event.button() == Qt.MouseButton.RightButton:
            if self.todo.isVisible():
                self.todo.hide()
            else:
                self.todo.show_near(
                    self.x(), self.y(),
                    self.width(), self.height()
                )