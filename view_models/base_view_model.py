from PySide6.QtCore import QObject

from core.mixins.log_mixin import LogMixin


class BaseViewModel(QObject, LogMixin):
    """
    모든 ViewModel의 기본 클래스이다.
    QObject를 상속받아 시그널/슬롯 기능을 지원한다.
    """

    def __init__(self):
        super().__init__()
        self.init_log_mixin()

