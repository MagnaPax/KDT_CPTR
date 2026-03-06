# main.py
"""
[메인 엔트리 포인트]

애플리케이션의 시작점이다.
"""
import sys
from dependency_injector.wiring import Provide, inject

from app.app_engine import AppEngine
from ui.main_window import MainWindow
from view_models.main_window_vm import MainViewModel
from core.di_container import AppContainer
from core.bootstrapper import AppBootstrapper


@inject
def main(
    # 컨테이너에서 팩토리/싱글톤을 찾아서 자동으로 넘겨줍니다.
    main_vm: MainViewModel = Provide[AppContainer.main_view_model],
    connection_manager = Provide[AppContainer.connection_manager]
):
    """
    앱의 진입 함수이다.
    """
    # 1. 앱 엔진 생성 (심장 이식)
    engine = AppEngine()

    # 2. 엔진 시동 
    engine.start()  # 초기화 (EventBus, LogListener 등)

    # 3. 부트스트래퍼(스플래시 화면 및 초기화 시퀀스) 시작
    bootstrapper = AppBootstrapper(connection_manager, main_vm)
    # GC(가비지 컬렉터)에 의한 소멸을 막기 위해 엔진에 참조를 유지시킴
    engine._bootstrapper = bootstrapper
    bootstrapper.run()

    # 4. 실제 이벤트 루프 진입
    sys.exit(engine.exec())


if __name__ == "__main__":
    # 프로그램이 시작될 때 단 한 번 컨테이너를 생성
    container = AppContainer()
    
    # 생성된 컨테이너와 현재 모듈(main.py)을 연결(Wiring)
    # 이 과정이 있어야 @inject 와 Provide 가 정상적으로 작동합니다.
    container.wire(modules=[__name__])
    
    main()
