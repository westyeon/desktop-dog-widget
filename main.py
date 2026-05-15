import sys
from PyQt6.QtWidgets import QApplication
from pet_widget import PetWidget
from tray_app import TrayApp


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet  = PetWidget()
    tray = TrayApp()

    # 신호 연결: tray에서 모드 바뀌면 → pet의 set_moving 호출
    # 이게 Qt의 Signal-Slot 패턴이야
    # "tray가 신호를 쏘면, pet이 받아서 처리"
    tray.movement_changed.connect(pet.set_moving)

    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()