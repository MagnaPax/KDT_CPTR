from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QDialog, QLabel, QProgressBar, QVBoxLayout, QHBoxLayout, 
    QWidget, QFrame, QGraphicsDropShadowEffect
)

class StartupSplash(QDialog):
    """
    고급스러운 다크 모드(HTML/Tailwind Inspired) 스플래시 스크린.
    아키텍처 부트스트래퍼(AppBootstrapper)가 호출하여 상태를 갱신한다.
    """
    def __init__(self):
        super().__init__()
        # 시스템 프레임 제거 및 항상 위에 표시
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint
        )
        self.setModal(True)
        # 배경을 투명하게 만들어 둥근 모서리(border-radius)가 먹히게 함
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # HTML 래퍼 느낌으로 크기 지정
        self.setFixedSize(700, 450)

        # 메인 레이아웃 (여백 0)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 둥근 모서리를 가진 뒷배경 컨테이너
        self.container = QFrame()
        self.container.setObjectName("SplashContainer")
        # 메인 배경색: #101922 (다크 블루/블랙계열)
        self.container.setStyleSheet("""
            QFrame#SplashContainer {
                background-color: #101922;
                border-radius: 12px;
                border: 1px solid #1e293b;
            }
        """)
        
        # 그림자 효과 부여 (glow 효과)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)

        # 컨테이너 내 레이아웃 구성
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        main_layout.addWidget(self.container)

        # 1. 헤더 (로고/앱 이름) 탑 여백
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 25, 30, 0)
        
        # 임시 아이콘 (파란 사각형)
        logo_label = QLabel()
        logo_label.setFixedSize(40, 40)
        logo_label.setStyleSheet("""
            background-color: rgba(13, 127, 242, 0.1); 
            border-radius: 8px;
            color: #0d7ff2;
            font-weight: bold;
            font-size: 20px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setText("⚡") # 임시 로고 아이콘
        
        title_label = QLabel("PLC Control")
        title_label.setStyleSheet("""
            color: #f1f5f9; 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            font-size: 20px; 
            font-weight: bold;
            letter-spacing: -0.5px;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(12)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        container_layout.addLayout(header_layout)

        # 2. 메인 컨텐츠 영역
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 60, 40, 60)
        content_layout.setAlignment(Qt.AlignCenter)
        
        self.main_status = QLabel("Initializing Connection")
        self.main_status.setAlignment(Qt.AlignCenter)
        self.main_status.setStyleSheet("""
            color: #f8fafc;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 34px;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        content_layout.addWidget(self.main_status)
        content_layout.addSpacing(40)
        
        # 현재 진행 중인 상태(Active Step) 박스 디자인
        self.step_box = QFrame()
        self.step_box.setFixedHeight(64)
        self.step_box.setStyleSheet("""
            QFrame {
                background-color: rgba(13, 127, 242, 0.1);
                border: 1px solid rgba(13, 127, 242, 0.3);
                border-radius: 8px;
            }
        """)
        step_layout = QHBoxLayout(self.step_box)
        step_layout.setContentsMargins(20, 0, 20, 0)
        
        # 좌측 파란색 상태 바(Accent) 수동 구현
        self.accent_bar = QFrame(self.step_box)
        self.accent_bar.setFixedSize(4, 64)
        self.accent_bar.move(0, 0)
        self.accent_bar.setStyleSheet("background-color: #0d7ff2; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border: none;")
        
        self.message_label = QLabel("초기화 준비 중...")
        self.message_label.setStyleSheet("""
            color: #0d7ff2;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 15px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)
        
        status_badge = QLabel("ACTIVE")
        status_badge.setStyleSheet("""
            color: #0d7ff2;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 1px;
            border: none;
            background: transparent;
        """)
        
        step_layout.addWidget(self.message_label)
        step_layout.addStretch()
        step_layout.addWidget(status_badge)
        
        content_layout.addWidget(self.step_box)

        container_layout.addLayout(content_layout)
        container_layout.addStretch()

        # 3. 바닥 프로그레스 바 (가장 얇게)
        self.progress_bar = QProgressBar()
        # 높이 조절
        self.progress_bar.setFixedHeight(6)
        # HTML 텍스트 비표시
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                margin: 0px;
            }
            QProgressBar::chunk {
                background-color: #0d7ff2;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        container_layout.addWidget(self.progress_bar)

    def update_progress(self, message: str, value: int) -> None:
        """Bootstrapper 측에서 상태변경 시 호출되는 API"""
        self.message_label.setText(message)
        self.progress_bar.setValue(max(0, min(100, value)))
        
        # 완료 시 메시지와 색상을 변경해준다
        if value >= 100:
            self.main_status.setText("Connection Established")
            self.step_box.setStyleSheet("""
                QFrame {
                    background-color: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 8px;
                }
            """)
            self.accent_bar.setStyleSheet("background-color: #10b981; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border: none;")
            self.message_label.setStyleSheet("color: #10b981; font-weight: 600; border: none; background: transparent;")
            self.progress_bar.setStyleSheet("""
                QProgressBar { background-color: #1e293b; border: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin: 0px; }
                QProgressBar::chunk { background-color: #10b981; border-radius: 3px; }
            """)
