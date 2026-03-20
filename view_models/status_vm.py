from PySide6.QtCore import Signal
from view_models.base_view_model import BaseViewModel

class StatusViewModel(BaseViewModel):
    """
    TwinCAT 연결 상태를 관리하여 UI(StatusWidget)에 전달하는 ViewModel
    """
    # UI에 보낼 시그널
    connection_state_changed = Signal(bool)

    def __init__(self, connection_manager=None):
        super().__init__()
        self.connection_manager = connection_manager
        
        # 외부 매니저의 신호 구독
        if self.connection_manager:
            self.connection_manager.connection_state_changed.connect(self._on_connection_changed)
    
    def _on_connection_changed(self, is_connected: bool):
        self.log_info(f"StatusViewModel: 연결 상태 변경됨 -> {is_connected}")
        # UI 쪽으로 위임 (위젯의 update_data 등에 연결됨)
        self.connection_state_changed.emit(is_connected)

    def get_current_state(self) -> bool:
        if self.connection_manager:
            return self.connection_manager.is_connected
        return False
