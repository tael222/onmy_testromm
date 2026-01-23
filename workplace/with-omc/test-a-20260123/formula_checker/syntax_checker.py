"""
Syntax Checker - Python 문법 오류 검사 모듈

Python 3.12 이상 기준으로 계산식 파일의 문법 오류를 검사합니다.
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class SyntaxError:
    """문법 오류 정보"""
    file_path: str
    line: int
    column: int
    message: str
    code_snippet: Optional[str] = None


@dataclass
class SyntaxCheckResult:
    """문법 검사 결과"""
    file_path: str
    is_valid: bool
    errors: list[SyntaxError]
    python_version: str


class SyntaxChecker:
    """Python 계산식 파일의 문법 검사를 수행하는 클래스"""

    MIN_PYTHON_VERSION = (3, 12)

    def __init__(self):
        self._check_python_version()

    def _check_python_version(self) -> None:
        """Python 버전 확인"""
        if sys.version_info < self.MIN_PYTHON_VERSION:
            raise RuntimeError(
                f"Python {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]} 이상이 필요합니다. "
                f"현재 버전: {sys.version_info.major}.{sys.version_info.minor}"
            )

    def check_file(self, file_path: str | Path) -> SyntaxCheckResult:
        """
        단일 파일의 문법 검사를 수행합니다.

        Args:
            file_path: 검사할 Python 파일 경로

        Returns:
            SyntaxCheckResult: 검사 결과
        """
        file_path = Path(file_path)
        errors = []

        if not file_path.exists():
            errors.append(SyntaxError(
                file_path=str(file_path),
                line=0,
                column=0,
                message=f"파일을 찾을 수 없습니다: {file_path}"
            ))
            return SyntaxCheckResult(
                file_path=str(file_path),
                is_valid=False,
                errors=errors,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}"
            )

        try:
            source_code = file_path.read_text(encoding="utf-8")
            ast.parse(source_code, filename=str(file_path))

            return SyntaxCheckResult(
                file_path=str(file_path),
                is_valid=True,
                errors=[],
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}"
            )

        except SyntaxError as e:
            code_lines = source_code.split("\n") if 'source_code' in locals() else []
            code_snippet = None
            if e.lineno and 0 < e.lineno <= len(code_lines):
                code_snippet = code_lines[e.lineno - 1]

            errors.append(SyntaxError(
                file_path=str(file_path),
                line=e.lineno or 0,
                column=e.offset or 0,
                message=e.msg or str(e),
                code_snippet=code_snippet
            ))

            return SyntaxCheckResult(
                file_path=str(file_path),
                is_valid=False,
                errors=errors,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}"
            )

    def check_source(self, source_code: str, filename: str = "<string>") -> SyntaxCheckResult:
        """
        소스 코드 문자열의 문법 검사를 수행합니다.

        Args:
            source_code: 검사할 Python 소스 코드
            filename: 오류 보고 시 사용할 파일명

        Returns:
            SyntaxCheckResult: 검사 결과
        """
        errors = []

        try:
            ast.parse(source_code, filename=filename)

            return SyntaxCheckResult(
                file_path=filename,
                is_valid=True,
                errors=[],
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}"
            )

        except SyntaxError as e:
            code_lines = source_code.split("\n")
            code_snippet = None
            if e.lineno and 0 < e.lineno <= len(code_lines):
                code_snippet = code_lines[e.lineno - 1]

            errors.append(SyntaxError(
                file_path=filename,
                line=e.lineno or 0,
                column=e.offset or 0,
                message=e.msg or str(e),
                code_snippet=code_snippet
            ))

            return SyntaxCheckResult(
                file_path=filename,
                is_valid=False,
                errors=errors,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}"
            )

    def check_directory(self, directory: str | Path, pattern: str = "*.py") -> list[SyntaxCheckResult]:
        """
        디렉토리 내 모든 Python 파일의 문법 검사를 수행합니다.

        Args:
            directory: 검사할 디렉토리 경로
            pattern: 파일 패턴 (기본값: *.py)

        Returns:
            list[SyntaxCheckResult]: 각 파일별 검사 결과 목록
        """
        directory = Path(directory)
        results = []

        for file_path in directory.rglob(pattern):
            results.append(self.check_file(file_path))

        return results
