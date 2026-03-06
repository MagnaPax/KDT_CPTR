"""
Low-level TwinCAT client wrapper.
Responsible for connect/disconnect and raw pyads communication only.
"""

from __future__ import annotations

import threading
from typing import Optional

from config.paths import TC_ADS_DLL_PATH
from core.devices.dll_loader import PyAdsDllLoader
from core.events.qt_bus import EVENT_BUS

_PYADS = None
_PYADS_LOCK = threading.Lock()


def _load_pyads():
    global _PYADS
    if _PYADS is not None:
        return _PYADS

    with _PYADS_LOCK:
        if _PYADS is None:
            PyAdsDllLoader(TC_ADS_DLL_PATH).load()
            import pyads as _pyads_module

            _PYADS = _pyads_module

    return _PYADS


class TwinCATClient:
    @staticmethod
    def ensure_driver_loaded() -> None:
        _load_pyads()

    def __init__(self, ams_net_id: str, port: Optional[int] = None):
        pyads = _load_pyads()
        self.ams_net_id = ams_net_id
        self.port = pyads.PORT_TC3PLC1 if port is None else port
        self.connection = None

    def connect(self) -> None:
        """Try connecting to TwinCAT (blocking)."""
        if self.connection and self.connection.is_open:
            return

        try:
            pyads = _load_pyads()
            self.connection = pyads.Connection(self.ams_net_id, self.port)
            self.connection.open()
            state = self.connection.read_state()
            EVENT_BUS.system.info.emit(
                f"TwinCAT 연결 성공: {self.ams_net_id}:{self.port} (State: {state})"
            )
        except Exception as exc:
            if self.connection:
                self.connection.close()
                self.connection = None
            raise ConnectionError(
                f"TwinCAT 연결 실패 ({self.ams_net_id}:{self.port}): {exc}"
            ) from exc

    def disconnect(self) -> None:
        """Disconnect TwinCAT safely."""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
                EVENT_BUS.system.info.emit(
                    f"TwinCAT 연결 해제 완료: {self.ams_net_id}"
                )
            except Exception as exc:
                EVENT_BUS.system.error.emit(f"TwinCAT 연결 해제 중 에러: {exc}")
            finally:
                self.connection = None

    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_open
