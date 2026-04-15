# core/mixins/log_mixin.py
"""
[로깅 Mixin]

EventBus 기반 로깅 기능을 제공하는 Mixin 클래스이다.
어떤 클래스든 이 Mixin을 상속받으면 self.log_info(), self.log_error() 등을 사용할 수 있다.

Mixin을 사용하는 이유:
    - BaseManager는 QObject를 상속
    - BaseView는 QWidget을 상속
    - 서로 다른 Qt 클래스를 상속하므로 공통 부모를 만들 수 없음
    - Mixin은 상속 체인과 무관하게 기능만 끼워넣음

사용법:
    from core.mixins.log_mixin import LogMixin

    class MyManager(QObject, LogMixin):
        def __init__(self):
            super().__init__()
            self.init_log_mixin()  # 로그 소스 자동 설정 (클래스 이름 사용)

        def some_method(self):
            self.log_info("작업 시작")
            self.log_error("에러 발생!")
"""
from __future__ import annotations

from core.events.qt_bus import EVENT_BUS


class LogMixin:
    """
    EventBus 기반 로깅 기능을 주입하는 Mixin.

    init_log_mixin()을 호출하면 log_source가 설정되며,
    호출하지 않아도 log() 메서드가 클래스 이름을 자동으로 사용한다.
    """

    def init_log_mixin(self, custom_source: str | None = None):
        """
        로그 소스 이름을 설정한다.
        custom_source를 주지 않으면 클래스 이름을 자동으로 사용한다.
        """
        self.log_source = custom_source or self.__class__.__name__

    # ==========================================================
    # 로깅 메서드
    # ==========================================================
    def log(self, message: str, level: str = "INFO"):
        """EventBus를 통해 로그를 전송한다."""
        source = getattr(self, "log_source", self.__class__.__name__)
        EVENT_BUS.log.message.emit(source, message, level)

    def log_info(self, message: str):
        self.log(message, "INFO")

    def log_warning(self, message: str):
        self.log(message, "WARNING")

    def log_error(self, message: str):
        self.log(message, "ERROR")

    def log_debug(self, message: str):
        self.log(message, "DEBUG")
