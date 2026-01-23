"""
Container Validator - 컨테이너 사용성 점검 모듈

DCN, DCR, DCP, DSP, DEP 등의 컨테이너가 올바른 ValueObject 타입을 사용하는지 확인합니다.
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ContainerType(Enum):
    """WAI 컨테이너 타입"""
    DCN = "DCN"  # Design Conditions
    DCR = "DCR"  # Design Criteria
    DCP = "DCP"  # Design Parameters
    DSP = "DSP"  # Design Spec Parameters
    DEP = "DEP"  # Design Equip Parameters
    STC = "STC"  # Structure
    EQP = "EQP"  # Equipment
    STD = "STD"  # Standard
    INF = "INF"  # Information
    MAP = "MAP"  # Mapping
    HWL = "HWL"  # Height Width Length
    OPX = "OPX"  # Operation Expense
    GV = "GV"    # Global Variables


class ValueObjectType(Enum):
    """WAI ValueObject 타입"""
    SINGLE_VALUE = "SingleValue"
    RANGED_VALUE = "RangedValue"
    TEXT_VALUE = "TextValue"
    BOOL_VALUE = "BoolValue"
    DROPBOX_VALUE = "DropboxValue"
    STRUCTURE_VALUE = "StructureValue"
    EQUIPMENT_VALUE = "EquipmentValue"
    PIPE_VALUE = "PipeValue"
    INFO_VALUE = "InfoValue"
    VECTOR2_VALUE = "Vector2Value"
    VECTOR3_VALUE = "Vector3Value"
    BOX2_VALUE = "Box2Value"
    BOX3_VALUE = "Box3Value"
    EL_BOX_VALUE = "ELBoxValue"
    STANDARD_TABLE = "StandardTable"
    INFO = "Info"


@dataclass
class ContainerUsage:
    """컨테이너 사용 정보"""
    container: ContainerType
    attribute_path: str  # 예: "influents.q"
    value_type: Optional[str]  # 할당된 ValueObject 타입
    line: int
    is_valid: bool
    issue: Optional[str] = None


@dataclass
class ContainerValidationResult:
    """컨테이너 검증 결과"""
    file_path: str
    is_valid: bool
    usages: list[ContainerUsage]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ContainerValidator:
    """컨테이너 사용성을 검증하는 클래스"""

    # 컨테이너별 허용되는 ValueObject 타입
    ALLOWED_VALUE_TYPES = {
        ContainerType.DCN: {
            ValueObjectType.SINGLE_VALUE,
            ValueObjectType.RANGED_VALUE,
            ValueObjectType.INFO_VALUE,
        },
        ContainerType.DCR: {
            ValueObjectType.SINGLE_VALUE,
            ValueObjectType.RANGED_VALUE,
        },
        ContainerType.DCP: {
            ValueObjectType.SINGLE_VALUE,
            ValueObjectType.RANGED_VALUE,
            ValueObjectType.TEXT_VALUE,
            ValueObjectType.BOOL_VALUE,
            ValueObjectType.DROPBOX_VALUE,
        },
        ContainerType.DSP: {
            ValueObjectType.SINGLE_VALUE,
            ValueObjectType.RANGED_VALUE,
            ValueObjectType.TEXT_VALUE,
            ValueObjectType.BOOL_VALUE,
            ValueObjectType.DROPBOX_VALUE,
        },
        ContainerType.DEP: {
            ValueObjectType.SINGLE_VALUE,
            ValueObjectType.RANGED_VALUE,
            ValueObjectType.TEXT_VALUE,
            ValueObjectType.BOOL_VALUE,
            ValueObjectType.DROPBOX_VALUE,
        },
        ContainerType.STC: {
            ValueObjectType.STRUCTURE_VALUE,
        },
        ContainerType.EQP: {
            ValueObjectType.EQUIPMENT_VALUE,
        },
        ContainerType.STD: {
            ValueObjectType.STANDARD_TABLE,
        },
        ContainerType.INF: {
            ValueObjectType.INFO,
        },
        ContainerType.HWL: {
            ValueObjectType.SINGLE_VALUE,
        },
        ContainerType.OPX: {
            ValueObjectType.SINGLE_VALUE,
        },
    }

    def __init__(self):
        self._container_names = {ct.value for ct in ContainerType}
        self._value_type_names = {vt.value for vt in ValueObjectType}

    def validate_file(self, file_path: str | Path) -> ContainerValidationResult:
        """
        파일의 컨테이너 사용성을 검증합니다.

        Args:
            file_path: 검증할 Python 파일 경로

        Returns:
            ContainerValidationResult: 검증 결과
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ContainerValidationResult(
                file_path=str(file_path),
                is_valid=False,
                usages=[],
                errors=[f"파일을 찾을 수 없습니다: {file_path}"]
            )

        source_code = file_path.read_text(encoding="utf-8")
        return self.validate_source(source_code, str(file_path))

    def validate_source(self, source_code: str, filename: str = "<string>") -> ContainerValidationResult:
        """
        소스 코드의 컨테이너 사용성을 검증합니다.

        Args:
            source_code: 검증할 Python 소스 코드
            filename: 파일명 (보고용)

        Returns:
            ContainerValidationResult: 검증 결과
        """
        usages = []
        errors = []
        warnings = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return ContainerValidationResult(
                file_path=filename,
                is_valid=False,
                usages=[],
                errors=[f"문법 오류: {e}"]
            )

        # 할당문 분석
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    usage = self._analyze_assignment(target, node.value, node.lineno)
                    if usage:
                        usages.append(usage)
                        if not usage.is_valid and usage.issue:
                            errors.append(f"Line {usage.line}: {usage.issue}")

        # 재할당 패턴 검증 (동적 값 반영)
        reassignment_warnings = self._check_reassignment_pattern(tree, source_code)
        warnings.extend(reassignment_warnings)

        is_valid = all(u.is_valid for u in usages) and len(errors) == 0

        return ContainerValidationResult(
            file_path=filename,
            is_valid=is_valid,
            usages=usages,
            errors=errors,
            warnings=warnings
        )

    def _analyze_assignment(
        self,
        target: ast.expr,
        value: ast.expr,
        line: int
    ) -> Optional[ContainerUsage]:
        """할당문을 분석하여 컨테이너 사용 정보를 추출합니다."""
        # 컨테이너 속성 할당 확인 (예: DCN.influents.q = ...)
        if not isinstance(target, ast.Attribute):
            return None

        attr_path = self._get_attribute_path(target)
        if not attr_path:
            return None

        parts = attr_path.split(".")
        if parts[0] not in self._container_names:
            return None

        try:
            container_type = ContainerType(parts[0])
        except ValueError:
            return None

        # 할당된 값의 타입 확인
        value_type = self._get_value_type(value)

        # 유효성 검증
        is_valid = True
        issue = None

        if value_type:
            try:
                vt = ValueObjectType(value_type)
                allowed = self.ALLOWED_VALUE_TYPES.get(container_type, set())
                if vt not in allowed:
                    is_valid = False
                    issue = f"{container_type.value}에 {value_type}는 허용되지 않습니다. 허용: {[v.value for v in allowed]}"
            except ValueError:
                # 알 수 없는 타입 (기본 타입 재할당 등)
                pass

        return ContainerUsage(
            container=container_type,
            attribute_path=".".join(parts[1:]),
            value_type=value_type,
            line=line,
            is_valid=is_valid,
            issue=issue
        )

    def _get_attribute_path(self, node: ast.expr) -> Optional[str]:
        """AST 노드에서 속성 경로를 추출합니다."""
        parts = []

        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value

        if isinstance(node, ast.Name):
            parts.append(node.id)
            parts.reverse()
            return ".".join(parts)

        return None

    def _get_value_type(self, node: ast.expr) -> Optional[str]:
        """할당된 값의 타입을 추출합니다."""
        # 함수 호출 (예: SingleValue(...))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return node.func.attr

        return None

    def _check_reassignment_pattern(self, tree: ast.AST, source_code: str) -> list[str]:
        """재할당 패턴을 검증하고 경고를 반환합니다."""
        warnings = []

        # ValueObject 첫 할당 후 동적 값 재할당 패턴 확인
        # 예: DSP.tank.volume = SingleValue(...) 후 DSP.tank.volume = calculated_value
        assignments = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    attr_path = self._get_attribute_path(target)
                    if attr_path:
                        parts = attr_path.split(".")
                        if parts[0] in self._container_names:
                            value_type = self._get_value_type(node.value)
                            if attr_path not in assignments:
                                assignments[attr_path] = []
                            assignments[attr_path].append({
                                "line": node.lineno,
                                "is_value_object": value_type in self._value_type_names
                            })

        # 패턴 분석
        for attr_path, assigns in assignments.items():
            if len(assigns) >= 2:
                first = assigns[0]
                if not first["is_value_object"]:
                    warnings.append(
                        f"Line {first['line']}: {attr_path}의 첫 할당이 ValueObject가 아닙니다. "
                        "재계산 시 TypeError가 발생할 수 있습니다."
                    )

        return warnings
