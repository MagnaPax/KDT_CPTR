from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from dependency_injector.wiring import Provide, inject

from core.di_container import AppContainer
from view_models.status_vm import StatusViewModel
from ui.widgets.base_widget import BaseWidget

class StatusWidget(BaseWidget[StatusViewModel]):
    """
    앱 하단 상태바 등에 들어갈 상태 표시 위젯.
    """
    @inject
    def __init__(self, view_model: StatusViewModel = Provide[AppContainer.status_view_model], parent=None):
        super().__init__(view_model, parent)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0)
        
        self.status_label = QLabel("DISCONNECTED")
        self.status_label.setObjectName("status_label")
        self.status_label.setProperty("status", "disconnected")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_label)

    def init_bindings(self):
        if self.view_model:
            # ViewModel의 시그널을 위젯의 데이터 갱신 메서드에 연결
            self.view_model.connection_state_changed.connect(self.safe_update_data)
            # 초기 상태 반영
            self.safe_update_data(self.view_model.get_current_state())

    def update_data(self, is_connected: bool):
        """BaseWidget의 추상 메서드 구현. safe_update_data를 거쳐 호출됨."""
        if is_connected:
            self.status_label.setText("CONNECTED")
            self.status_label.setProperty("status", "connected")
        else:
            self.status_label.setText("DISCONNECTED")
            self.status_label.setProperty("status", "disconnected")
        
        # QSS 속성이 바뀌었으므로 다시 렌더링하도록 갱신
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
