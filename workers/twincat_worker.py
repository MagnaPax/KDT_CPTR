# workers/twincat_worker.py
from PySide6.QtCore import Signal, QThread
from workers.base_worker import BaseWorker
from core.devices.twincat_client import TwinCATClient

class TwinCATConnectWorker(BaseWorker):
    """
    TwinCAT 연결을 시도하는 비동기 워커.
    연결 성공 시 connection_established 시그널로 연결된 Client 객체를 상위로 전달한다.
    """
    
    # 연결 성공 시 방출할 커스텀 시그널
    connection_established = Signal(object) 
    
    def __init__(self, ams_net_id: str):
        super().__init__()
        self.ams_net_id = ams_net_id
        self.client = TwinCATClient(self.ams_net_id)

    def process(self):
        """실제 백그라운드 스레드에서 돌아가는 연결 부"""
        
        self.log_info(f"TwinCAT 연결 시도 중 ({self.ams_net_id})...")
        
        # 외부에서 취소 요청이 들어왔는지 루프/실행 전 확인
        if QThread.currentThread().isInterruptionRequested():
            self.log_warning("연결 시작 전 취소됨.")
            return

        try:
            # 타임아웃/블로킹이 발생할 수 있는 실제 연결 함수
            self.client.connect()
            
            # 취소 요건 재확인 (연결 도중에 취소 눌렀을 경우)
            if QThread.currentThread().isInterruptionRequested():
                self.log_warning("연결 성공했으나 취소되어 즉시 접속 종료함.")
                self.client.disconnect()
                return

            self.log_info("TwinCAT 연결 성공!")
            self.connection_established.emit(self.client)
            
        except Exception as e:
            # 상세 에러 로그 기록 후 상위(BaseWorker)로 위임
            # BaseWorker.process 의 try-except 블록이 잡아 worker_failed 시그널로 변환함
            raise
            
    def stop_custom_resources(self):
        """사용자가 '비상정지/강제취소' 버튼을 눌렀을 때 진행 중인 소켓 닫기"""
        if self.client and self.client.is_connected():
            self.client.disconnect()
