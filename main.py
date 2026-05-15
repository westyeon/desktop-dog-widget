import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from pet_widget import PetWidget
from tray_app import TrayApp
from scheduler import Scheduler


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet   = PetWidget()
    tray  = TrayApp()
    sched = Scheduler()

    tray.movement_changed.connect(pet.set_moving)
    sched.notify.connect(pet.show_notification)

    # ← 핵심: 앱이 비활성화돼도 강아지 계속 표시
    app.applicationStateChanged.connect(
        lambda state: pet.show() if pet.isVisible() or True else None
    )

    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()