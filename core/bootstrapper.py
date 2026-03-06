import sys
from PySide6.QtCore import QObject, QTimer
from core.events.qt_bus import EVENT_BUS
from ui.splash_screen import StartupSplash
from ui.main_window import MainWindow

class AppBootstrapper(QObject):
    """
    애플리케이션의 뼈대 조립과 부팅 시나리오를 지휘하는 오케스트레이터.
    스플래시 화면 띄우기 -> TwinCAT 연결 -> 메인 윈도우 전환의 흐름을 관리한다.
    """
    def __init__(self, connection_manager, main_view_model):
        super().__init__()
        self.connection_manager = connection_manager
        self.main_view_model = main_view_model
        
        self.splash = StartupSplash()
        
        # 시스템 이벤트를 구독하여 스플래시 화면에 상황 중계
        EVENT_BUS.system.info.connect(self._on_system_info)
        EVENT_BUS.system.error.connect(self._on_system_error)
        
        # TwinCAT 상태 구독
        self.connection_manager.connection_state_changed.connect(self._on_connection_result)
        
    def run(self):
        self.splash.show()
        self.splash.update_progress("TwinCAT 연결 준비 중...", 10)
        
        # UI 이벤트 루프가 스플래시 화면을 먼저 그릴 시간을 조금 준 뒤 백그라운드 워커 시작
        QTimer.singleShot(100, self.connection_manager.request_connection)
        
    def _on_system_info(self, msg: str):
        # 메시지를 받으면 프로그레스 바를 임의의 50%로 맞추며 상태 표시
        if "TwinCAT 연결 성공" not in msg:
            self.splash.update_progress(msg, 50)
            
    def _on_system_error(self, msg: str):
        self.splash.update_progress(msg, 100)
        
    def _on_connection_result(self, is_connected: bool):
        if is_connected:
            self.splash.update_progress("TwinCAT 연결 성공!", 100)
            # 연결 성공 창을 잠깐(0.5초) 보여주고 메인 화면으로 전환
            QTimer.singleShot(500, self._start_main_window)
        else:
            self.splash.update_progress("TwinCAT 연결 실패!", 100)
            EVENT_BUS.system.error.emit("TwinCAT 연결 실패. 로그를 확인하세요.")
            # 연결 실패 시 2초 뒤 앱 자동 종료 처리 (UX상 에러 메시지를 볼 시간을 준다)
            QTimer.singleShot(2000, lambda: sys.exit(1))
            
    def _start_main_window(self):
        self.splash.close()
        # MainWindow 생성 시 주입받아둔 뷰모델을 꽂아넣는다.
        # (MainWindow 내부 구조에 따라 connection_manager도 전달 가능)
        self.main_window = MainWindow(self.main_view_model, self.connection_manager)
        self.main_window.show()
