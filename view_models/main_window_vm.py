from view_models.base_view_model import BaseViewModel

class MainViewModel(BaseViewModel):
    """
    메인 윈도우의 비즈니스 로직과 상태를 관리하는 ViewModel
    """
    def __init__(self, system_manager=None, connection_manager=None):
        super().__init__()
        # 상태 관리를 담당하는 매니저를 외부(main.py)로부터 주입받아 저장한다 (Has-A 관계)
        self.system_manager = system_manager
        self.connection_manager = connection_manager
        
        self.log_info("MainViewModel 초기화됨")

        if self.connection_manager:
            self.connection_manager.connection_state_changed.connect(self._on_connection_changed)

    def _on_connection_changed(self, is_connected: bool):
        if is_connected:
            self.log_info("ViewModel: TwinCAT 연결됨")
        else:
            self.log_info("ViewModel: TwinCAT 연결 끊김")
