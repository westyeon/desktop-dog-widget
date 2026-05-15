# 🐾 Desktop Dog Widget

화면 위를 자유롭게 이동하는 데스크탑 펫 애플리케이션

## 미리보기
<img src="example_photo/example.png" width="200"/>

## 소개
직접 그린 강아지 캐릭터가 바탕화면을 돌아다니며 할일을 알려주는 데스크탑 위젯입니다.

## 기능
- 🐕 강아지 캐릭터 애니메이션 (걷기 / 서있기 / 눕기)
- ✅ 우클릭으로 할일 등록 · 체크 · 삭제
- 💬 미완료 할일을 말풍선으로 상시 표시
- ⏰ 일정 등록 및 N분 전 알림
- 🖥️ 메뉴바에서 이동 모드 전환 (돌아다니기 / 가만히 있기)

## 실행 방법

### 요구사항
- Python 3.11 이상

### 설치 및 실행
```bash
git clone https://github.com/westyeon/desktop-dog-widget.git
cd desktop-dog-widget
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

## 기술 스택
| 항목 | 내용 |
|---|---|
| Language | Python 3.11 |
| GUI | PyQt6 |
| 애니메이션 | QTimer |
| 데이터 저장 | JSON |
| 배포 | PyInstaller (macOS / Windows) |

## 개발 환경
- macOS
- Visual Studio Code
