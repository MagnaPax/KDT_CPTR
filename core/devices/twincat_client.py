# core/devices/twincat_client.py
"""
TwinCAT 통신의 최하단 인프라
오직 연결(connect), 해제(disconnect), 그리고 원시 통신(pyads)만 책임진다.
"""
from typing import Optional

from config.paths import TC_ADS_DLL_PATH
from core.devices.dll_loader import PyAdsDllLoader

# pyads 모듈이 내부적으로 C 라이브러리를 바인딩하므로, 임포트 전에 DLL을 먼저 메모리에 올린다.
PyAdsDllLoader(TC_ADS_DLL_PATH).load()

import pyads

from core.events.qt_bus import EVENT_BUS

class TwinCATClient:
    def __init__(self, ams_net_id: str, port: int = pyads.PORT_TC3PLC1):
        self.ams_net_id = ams_net_id
        self.port = port
        self.connection: Optional[pyads.Connection] = None

    def connect(self):
        """TwinCAT 연결 시도 (블로킹 동작)"""
        if self.connection and self.connection.is_open:
            return # 이미 연결됨

        try:
            self.connection = pyads.Connection(self.ams_net_id, self.port)
            self.connection.open()
            
            # 연결 확인용 간단한 핑 (디바이스 상태 읽기)
            # 상태 코드를 읽을 수 있다면 물리적 연결이 정상임을 보장한다.
            state = self.connection.read_state()
            EVENT_BUS.system.info.emit(f"TwinCAT 연결 성공: {self.ams_net_id}:{self.port} (State: {state})")
            
        except Exception as e:
            if self.connection:
                self.connection.close()
                self.connection = None
            raise ConnectionError(f"TwinCAT 연결 실패 ({self.ams_net_id}:{self.port}): {e}")

    def disconnect(self):
        """TwinCAT 연결 해제"""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
                EVENT_BUS.system.info.emit(f"TwinCAT 연결 해제 완료: {self.ams_net_id}")
            except Exception as e:
                EVENT_BUS.system.error.emit(f"TwinCAT 연결 해제 중 에러: {e}")
            finally:
                self.connection = None

    def is_connected(self) -> bool:
        """연결 상태 반환"""
        return self.connection is not None and self.connection.is_open
