"""
scheduler.py
30초마다 등록된 일정을 체크해서 알림 시간이 되면 신호를 보냄.

왜 APScheduler 대신 QTimer?
→ APScheduler는 별도 스레드를 쓰는데 PyQt6와 함께 쓰면
  UI 업데이트를 메인 스레드에서 해야 해서 복잡해짐.
  QTimer는 메인 이벤트 루프에서 돌아서 안전하고 간단함.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from datetime import datetime, timedelta
import storage


class Scheduler(QObject):
    # 알림 발생 시 메시지 문자열을 담아 emit
    notify = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 이미 알림 보낸 항목 기록 (앱 재시작 전까지 중복 방지)
        # key = "schedule_id_notify분"
        self._notified = set()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check)
        self.timer.start(30_000)  # 30초마다 체크

        # 시작하자마자 한 번 즉시 체크
        self._check()

    def _check(self):
        now = datetime.now()
        for s in storage.load_schedules():
            for mins in s.get("notify_minutes", [10]):
                key = f"{s['id']}_{mins}"
                if key in self._notified:
                    continue

                # 오늘 기준 일정 시각
                try:
                    target = now.replace(
                        hour=s["hour"], minute=s["minute"],
                        second=0, microsecond=0
                    )
                except ValueError:
                    continue

                notify_at = target - timedelta(minutes=mins)
                diff = abs((now - notify_at).total_seconds())

                # 알림 시각 ±30초 이내면 발송
                if diff <= 30:
                    title = s.get("title", "일정")
                    hour  = s["hour"]
                    minute = s["minute"]
                    time_str = f"{hour}시" + (f" {minute}분" if minute else "")
                    msg = f"⏰ {time_str} '{title}' {mins}분 전이에요!"
                    self.notify.emit(msg)
                    self._notified.add(key)