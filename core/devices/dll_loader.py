# core/devices/dll_loader.py
"""
pyads 라이브러리를 사용하기 위한 DLL 로더 클래스

- OS가 Windows일 때 Beckhoff TcAdsDll.dll 로드
- 파일 존재 여부 확인은 utilities.file_handler에 위임
- 성공/실패 시 예외 처리
"""

import os
import ctypes
import platform
from pathlib import Path

from utilities.file_handler import load_text # 파일 존재 여부 확인용 (예외 처리 활용)
from utilities.file_exceptions import FileOperationError

class PyAdsDllLoader:
    def __init__(self, dll_path: Path):
        self.dll_path = dll_path

    def load(self) -> None:
        """
        TcAdsDll.dll 로드

        동작:
            - Windows가 아니면 바로 리턴
            - 파일이 없으면 FileOperationError 발생
            - 로드 실패 시 OSError 발생
        """
        # 1. OS 체크
        if platform.system() != 'Windows':
            return
            
        # 2. 파일 존재 여부 확인 (file_handler 활용)
        if not self.dll_path.exists():
            raise FileNotFoundError(f"DLL 파일을 찾을 수 없다: {self.dll_path}")

        # 3. DLL 로드
        try:
            dll_directory = self.dll_path.parent
            os.add_dll_directory(str(dll_directory))
            ctypes.windll.LoadLibrary(str(self.dll_path))
        except Exception as e:
            raise OSError(f"DLL 로드 실패: {e}")
