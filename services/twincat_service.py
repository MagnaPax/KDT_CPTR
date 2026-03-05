# services/twincat_service.py
from typing import Optional

from PySide6.QtCore import Signal

from services.base_service import BaseService
from workers.twincat_worker import TwinCATConnectWorker
from core.devices.twincat_client import TwinCATClient

class TwinCATService(BaseService):
    """
    TwinCAT 워커들을 스레드에 태워 실행하고, 연결 상태를 관리하는 서비스.
    ViewModel이나 Manager의 요청을 받아 백그라운드 작업을 조율한다.
    """
    
    # 워커의 결과를 상위 매니저/뷰모델로 릴레이
    connection_success = Signal(object) # TwinCATClient 객체
    connection_failed = Signal(str)     # Error Msg
    
    def __init__(self):
        super().__init__()
        self.active_client: Optional[TwinCATClient] = None
        
    def start_connection(self, ams_net_id: str):
        """백그라운드 스레드에서 TwinCAT 연결 작업을 시작한다."""
        self.log_info(f"TwinCAT 연결 작업(워커) 지시: {ams_net_id}")
        
        # 1. 일꾼 생성
        worker = TwinCATConnectWorker(ams_net_id)
        
        # 2. 일꾼의 통신선(시그널) 연결
        worker.connection_established.connect(self._on_connection_success)
        worker.worker_failed.connect(self._on_connection_failed)
        
        # 3. 서비스(공장)에 일꾼을 스레드에 태워 실행해달라고 위탁
        # worker_id를 지정하여 나중에 통제(취소/강제종료) 가능하게 함
        # force_interrupt=True로 똑같은 연결 시도가 연달아 들어오면 기존 것을 폐기하고 새 시도를 우선함.
        self.start_worker(
            worker=worker,
            worker_id="TC_CONNECT_TASK",
            force_interrupt=True
        )

    def cancel_connection(self):
        """연결 시도를 도중에 취소한다."""
        self.stop_worker("TC_CONNECT_TASK")

    def disconnect_active_client(self):
        """현재 연결된 소켓을 안전하게 닫는다."""
        if self.active_client:
            self.active_client.disconnect()
            self.active_client = None
            self.log_info("활성화된 TwinCAT 소켓을 닫았습니다.")

    # ============================
    # 내부 워커 이벤트 핸들러
    # ============================
    def _on_connection_success(self, client: TwinCATClient):
        self.active_client = client  # 살아있는 소켓 킵
        self.connection_success.emit(self.active_client)

    def _on_connection_failed(self, err_msg: str):
        self.active_client = None
        self.connection_failed.emit(err_msg)
