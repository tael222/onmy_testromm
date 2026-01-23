"""
Function Validator - 필수 함수 정의 여부 확인 모듈

계산식 종류에 따라 필수 함수가 정의되어 있는지 검증합니다.
- Structure: forward_calculate, reverse_calculate, level_calculate
- Equipment: forward_calculate
- Process: 특정 함수 요구 없음
"""

import ast
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FormulaType(Enum):
    """계산식 종류"""
    PROCESS = "process"
    STRUCTURE = "structure"
    EQUIPMENT = "equipment"


@dataclass
class FunctionInfo:
    """함수 정보"""
    name: str
    line: int
    parameters: list[str]
    has_return: bool


@dataclass
class FunctionValidationResult:
    """함수 검증 결과"""
    file_path: str
    formula_type: FormulaType
    is_valid: bool
    found_functions: list[FunctionInfo]
    missing_functions: list[str]
    extra_info: dict = field(default_factory=dict)


class FunctionValidator:
    """계산식 파일의 필수 함수 정의 여부를 검증하는 클래스"""

    REQUIRED_FUNCTIONS = {
        FormulaType.STRUCTURE: ["forward_calculate", "reverse_calculate", "level_calculate"],
        FormulaType.EQUIPMENT: ["forward_calculate"],
        FormulaType.PROCESS: [],  # Process는 필수 함수 없음
    }

    def __init__(self):
        pass

    def _extract_functions(self, source_code: str) -> list[FunctionInfo]:
        """소스 코드에서 함수 정의를 추출합니다."""
        functions = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return functions

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                has_return = any(
                    isinstance(stmt, ast.Return) and stmt.value is not None
                    for stmt in ast.walk(node)
                )

                functions.append(FunctionInfo(
                    name=node.name,
                    line=node.lineno,
                    parameters=params,
                    has_return=has_return
                ))

        return functions

    def validate_file(
        self,
        file_path: str | Path,
        formula_type: FormulaType
    ) -> FunctionValidationResult:
        """
        파일의 필수 함수 정의 여부를 검증합니다.

        Args:
            file_path: 검증할 Python 파일 경로
            formula_type: 계산식 종류

        Returns:
            FunctionValidationResult: 검증 결과
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return FunctionValidationResult(
                file_path=str(file_path),
                formula_type=formula_type,
                is_valid=False,
                found_functions=[],
                missing_functions=self.REQUIRED_FUNCTIONS[formula_type],
                extra_info={"error": f"파일을 찾을 수 없습니다: {file_path}"}
            )

        source_code = file_path.read_text(encoding="utf-8")
        return self.validate_source(source_code, str(file_path), formula_type)

    def validate_source(
        self,
        source_code: str,
        filename: str,
        formula_type: FormulaType
    ) -> FunctionValidationResult:
        """
        소스 코드의 필수 함수 정의 여부를 검증합니다.

        Args:
            source_code: 검증할 Python 소스 코드
            filename: 파일명 (보고용)
            formula_type: 계산식 종류

        Returns:
            FunctionValidationResult: 검증 결과
        """
        found_functions = self._extract_functions(source_code)
        found_names = {f.name for f in found_functions}

        required = self.REQUIRED_FUNCTIONS[formula_type]
        missing = [name for name in required if name not in found_names]

        return FunctionValidationResult(
            file_path=filename,
            formula_type=formula_type,
            is_valid=len(missing) == 0,
            found_functions=found_functions,
            missing_functions=missing
        )

    def detect_formula_type(self, source_code: str) -> Optional[FormulaType]:
        """
        소스 코드에서 계산식 종류를 추론합니다.

        Args:
            source_code: Python 소스 코드

        Returns:
            FormulaType: 추론된 계산식 종류 (추론 불가 시 None)
        """
        found_functions = self._extract_functions(source_code)
        found_names = {f.name for f in found_functions}

        # Structure: 3개 함수 모두 있음
        structure_funcs = set(self.REQUIRED_FUNCTIONS[FormulaType.STRUCTURE])
        if structure_funcs.issubset(found_names):
            return FormulaType.STRUCTURE

        # Equipment: forward_calculate만 있고 나머지 없음
        if "forward_calculate" in found_names:
            if "reverse_calculate" not in found_names and "level_calculate" not in found_names:
                return FormulaType.EQUIPMENT

        # Process: WAI 컨테이너 import 확인
        if self._has_wai_imports(source_code):
            return FormulaType.PROCESS

        return None

    def _has_wai_imports(self, source_code: str) -> bool:
        """WAI 모듈 import 여부 확인"""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "WAI" or alias.name.startswith("WAI."):
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == "WAI" or node.module.startswith("WAI.")):
                    return True

        return False

    def get_function_signature(self, func_info: FunctionInfo) -> str:
        """함수 시그니처 문자열 생성"""
        params = ", ".join(func_info.parameters)
        return f"def {func_info.name}({params})"
