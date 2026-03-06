# managers/connection_manager.py
"""
통신 연결(상태 추적, 재시도, 에러 처리) 등 전체 시스템의 통신 생명주기를 주관.
ViewModel은 이 Manager를 주입받아 쓰거나 EventBus를 구독한다.
"""
from PySide6.QtCore import QObject, QTimer, Signal

from core.events.qt_bus import EVENT_BUS
from managers.base_manager import BaseManager
from services.twincat_service import TwinCATService

class ConnectionManager(BaseManager):
    # 연결 상태 변경 시그널 (ViewModel 연결용)
    connection_state_changed = Signal(bool) # True면 연결됨, False면 끊김
    
    def __init__(self, ams_net_id: str, port: int = 851):
        super().__init__()
        self.ams_net_id = ams_net_id
        self.port = port
        
        # 실제 워커 스레드를 돌려줄 서비스 인스턴스 소유
        self.twincat_service = TwinCATService()
        
        # 서비스의 결과(워커 완료/실패)를 Manager의 귀(콜백)에 연결
        self.twincat_service.connection_success.connect(self._on_service_connected)
        self.twincat_service.connection_failed.connect(self._on_service_failed)
        
        # 상태 속성
        self.is_connected = False
        
        # 재시도 관련
        self.retry_count = 0
        self.max_retries = 3
        
        # 논블로킹 딜레이를 위한 타이머
        self.retry_timer = QTimer(self)
        self.retry_timer.setSingleShot(True)
        self.retry_timer.timeout.connect(self._do_connect)


    def request_connection(self):
        """외부(스플래시나 UI 버튼)에서 연결을 요청하는 진입점"""
        self.retry_count = 0
        self._do_connect()

    def disconnect_all(self):
        """앱 종료나 수동 끊기 시 호출"""
        self.retry_timer.stop()
        self.twincat_service.cancel_connection()
        self.twincat_service.disconnect_active_client()
        self._set_state_disconnected()

    # ============================
    # 내부 로직
    # ============================
    def _do_connect(self):
        self.retry_count += 1
        msg = f"TwinCAT 연결 시도 중... ({self.retry_count}/{self.max_retries})"

        # 1. 파일과 터미널에 기록 (BaseManager의 기능 상속)
        self.log_info(msg)

        # 2. 로딩 창이나 UI 상태바에 알림 (System 채널 방송)
        EVENT_BUS.system.info.emit(msg) 
        
        # 서비스야, 워커 만들어서 연결 시작해라.
        self.twincat_service.start_connection(self.ams_net_id, self.port)


    def _on_service_connected(self, client_instance):
        """서비스(워커)가 연결에 성공했을 때"""
        self.retry_count = 0
        self.is_connected = True
        
        EVENT_BUS.system.info.emit("TwinCAT 장비와 통신이 수립되었습니다.")
        
        # UI들(ViewModel)에게 '나 성공했어 녹색 불 켜!' 라고 시그널 쏴줌
        self.connection_state_changed.emit(True)


    def _on_service_failed(self, error_msg: str):
        """서비스(워커)가 연결에 실패하거나 예외가 났을 때"""
        
        if self.retry_count < self.max_retries:
            EVENT_BUS.system.warning.emit(f"연결 실패, 단기 재시도 대기 중: {error_msg}")
            # 스레드를 멈추지(Sleep) 않고 이벤트 루프를 통해 2초 뒤 재시도
            self.retry_timer.start(2000) 
        else:
            EVENT_BUS.system.error.emit(f"최대 연결 재시도 횟수 초과. 연결 불가: {error_msg}")
            self._set_state_disconnected()

    def _set_state_disconnected(self):
        self.is_connected = False
        self.connection_state_changed.emit(False)
