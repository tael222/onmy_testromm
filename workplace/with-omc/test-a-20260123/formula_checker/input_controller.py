"""
Input Controller - 입력 및 출력 제어 모듈

Unity 없이 DCN, DSP, DEP 등 입력 컨테이너 값을 직접 정의하고
계산 결과를 확인할 수 있는 기능을 제공합니다.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from datetime import datetime


@dataclass
class InputDefinition:
    """입력값 정의"""
    container: str  # DCN, DSP, DEP 등
    path: str       # 예: influents.q
    name: str
    value: float | int | str | bool
    unit: str = ""
    editable: bool = True
    remark: str = ""


@dataclass
class OutputValue:
    """출력값"""
    container: str
    path: str
    name: str
    value: Any
    unit: str = ""


@dataclass
class TestCase:
    """테스트 케이스"""
    name: str
    description: str
    inputs: list[InputDefinition]
    expected_outputs: list[OutputValue] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionSummary:
    """실행 결과 요약"""
    test_case_name: str
    success: bool
    inputs_applied: int
    outputs_captured: int
    duration_ms: float
    errors: list[str] = field(default_factory=list)
    outputs: list[OutputValue] = field(default_factory=list)


class InputController:
    """입력값 제어 및 출력값 확인을 위한 컨트롤러"""

    def __init__(self):
        self._inputs: list[InputDefinition] = []
        self._outputs: list[OutputValue] = []
        self._test_cases: dict[str, TestCase] = {}

    def define_input(
        self,
        container: str,
        path: str,
        name: str,
        value: float | int | str | bool,
        unit: str = "",
        editable: bool = True,
        remark: str = ""
    ) -> InputDefinition:
        """
        입력값을 정의합니다.

        Args:
            container: 컨테이너 이름 (DCN, DSP, DEP 등)
            path: 속성 경로 (예: influents.q)
            name: 값 이름
            value: 값
            unit: 단위
            editable: 편집 가능 여부
            remark: 비고

        Returns:
            InputDefinition: 정의된 입력값
        """
        input_def = InputDefinition(
            container=container,
            path=path,
            name=name,
            value=value,
            unit=unit,
            editable=editable,
            remark=remark
        )
        self._inputs.append(input_def)
        return input_def

    def define_inputs_batch(self, inputs: list[dict]) -> list[InputDefinition]:
        """
        여러 입력값을 일괄 정의합니다.

        Args:
            inputs: 입력값 딕셔너리 목록

        Returns:
            list[InputDefinition]: 정의된 입력값 목록
        """
        defined = []
        for inp in inputs:
            defined.append(self.define_input(**inp))
        return defined

    def clear_inputs(self) -> None:
        """정의된 입력값을 모두 삭제합니다."""
        self._inputs = []

    def get_inputs(self) -> list[InputDefinition]:
        """정의된 입력값 목록을 반환합니다."""
        return self._inputs.copy()

    def create_test_case(
        self,
        name: str,
        description: str,
        inputs: Optional[list[InputDefinition]] = None
    ) -> TestCase:
        """
        테스트 케이스를 생성합니다.

        Args:
            name: 테스트 케이스 이름
            description: 설명
            inputs: 입력값 목록 (None이면 현재 정의된 입력값 사용)

        Returns:
            TestCase: 생성된 테스트 케이스
        """
        test_case = TestCase(
            name=name,
            description=description,
            inputs=inputs if inputs is not None else self._inputs.copy()
        )
        self._test_cases[name] = test_case
        return test_case

    def save_test_case(self, test_case: TestCase, file_path: str | Path) -> None:
        """
        테스트 케이스를 JSON 파일로 저장합니다.

        Args:
            test_case: 저장할 테스트 케이스
            file_path: 저장 경로
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "name": test_case.name,
            "description": test_case.description,
            "created_at": test_case.created_at,
            "inputs": [asdict(inp) for inp in test_case.inputs],
            "expected_outputs": [asdict(out) for out in test_case.expected_outputs]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_test_case(self, file_path: str | Path) -> TestCase:
        """
        JSON 파일에서 테스트 케이스를 로드합니다.

        Args:
            file_path: 로드할 파일 경로

        Returns:
            TestCase: 로드된 테스트 케이스
        """
        file_path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        inputs = [InputDefinition(**inp) for inp in data.get("inputs", [])]
        expected_outputs = [OutputValue(**out) for out in data.get("expected_outputs", [])]

        test_case = TestCase(
            name=data["name"],
            description=data["description"],
            inputs=inputs,
            expected_outputs=expected_outputs,
            created_at=data.get("created_at", "")
        )

        self._test_cases[test_case.name] = test_case
        return test_case

    def apply_inputs_to_runner(self, runner: Any) -> int:
        """
        정의된 입력값을 IntegrationRunner에 적용합니다.

        Args:
            runner: IntegrationRunner 인스턴스

        Returns:
            int: 적용된 입력값 수
        """
        from .integration_runner import SingleValue, RangedValue

        applied = 0

        for inp in self._inputs:
            container = runner.wai.get_container(inp.container)

            # 경로 파싱 및 설정
            parts = inp.path.split(".")
            target = container

            for part in parts[:-1]:
                if not hasattr(target, part):
                    setattr(target, part, type(target)())
                target = getattr(target, part)

            # 값 설정
            final_key = parts[-1]
            value_obj = SingleValue(
                name=inp.name,
                value=inp.value,
                editable=inp.editable,
                unit=inp.unit,
                remark=inp.remark
            )
            setattr(target, final_key, value_obj)
            applied += 1

        return applied

    def capture_outputs(self, runner: Any, paths: list[tuple[str, str]]) -> list[OutputValue]:
        """
        실행 결과에서 지정된 출력값을 캡처합니다.

        Args:
            runner: IntegrationRunner 인스턴스
            paths: (컨테이너, 경로) 튜플 목록

        Returns:
            list[OutputValue]: 캡처된 출력값 목록
        """
        outputs = []

        for container_name, path in paths:
            container = runner.wai.get_container(container_name)

            # 경로 파싱
            parts = path.split(".")
            target = container

            try:
                for part in parts:
                    target = getattr(target, part)

                # 값 추출
                if hasattr(target, "value"):
                    value = target.value
                    name = getattr(target, "name", path)
                    unit = getattr(target, "unit", "")
                else:
                    value = target
                    name = path
                    unit = ""

                outputs.append(OutputValue(
                    container=container_name,
                    path=path,
                    name=name,
                    value=value,
                    unit=unit
                ))

            except AttributeError:
                outputs.append(OutputValue(
                    container=container_name,
                    path=path,
                    name=path,
                    value=None,
                    unit=""
                ))

        self._outputs = outputs
        return outputs

    def compare_outputs(
        self,
        actual: list[OutputValue],
        expected: list[OutputValue],
        tolerance: float = 1e-6
    ) -> tuple[bool, list[str]]:
        """
        실제 출력값과 기대 출력값을 비교합니다.

        Args:
            actual: 실제 출력값
            expected: 기대 출력값
            tolerance: 숫자 비교 허용 오차

        Returns:
            tuple[bool, list[str]]: (일치 여부, 불일치 목록)
        """
        mismatches = []

        expected_dict = {(e.container, e.path): e for e in expected}

        for act in actual:
            key = (act.container, act.path)
            if key in expected_dict:
                exp = expected_dict[key]

                if isinstance(act.value, (int, float)) and isinstance(exp.value, (int, float)):
                    if abs(act.value - exp.value) > tolerance:
                        mismatches.append(
                            f"{act.container}.{act.path}: 기대값 {exp.value}, 실제값 {act.value}"
                        )
                elif act.value != exp.value:
                    mismatches.append(
                        f"{act.container}.{act.path}: 기대값 {exp.value}, 실제값 {act.value}"
                    )

        return len(mismatches) == 0, mismatches

    def format_outputs(self, outputs: list[OutputValue]) -> str:
        """출력값을 포맷팅된 문자열로 반환합니다."""
        lines = ["=" * 60, "계산 결과", "=" * 60]

        for out in outputs:
            unit_str = f" {out.unit}" if out.unit else ""
            lines.append(f"  {out.container}.{out.path}: {out.value}{unit_str}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def generate_report(
        self,
        test_case: TestCase,
        summary: ExecutionSummary,
        detailed: bool = True
    ) -> str:
        """
        테스트 결과 리포트를 생성합니다.

        Args:
            test_case: 테스트 케이스
            summary: 실행 요약
            detailed: 상세 정보 포함 여부

        Returns:
            str: 리포트 문자열
        """
        lines = [
            "=" * 70,
            f"테스트 케이스: {test_case.name}",
            f"설명: {test_case.description}",
            "=" * 70,
            "",
            f"실행 결과: {'성공' if summary.success else '실패'}",
            f"소요 시간: {summary.duration_ms:.2f}ms",
            f"입력값: {summary.inputs_applied}개",
            f"출력값: {summary.outputs_captured}개",
            "",
        ]

        if summary.errors:
            lines.append("오류:")
            for err in summary.errors:
                lines.append(f"  - {err}")
            lines.append("")

        if detailed and summary.outputs:
            lines.append("출력값:")
            for out in summary.outputs:
                unit_str = f" {out.unit}" if out.unit else ""
                lines.append(f"  {out.container}.{out.path}: {out.value}{unit_str}")

        lines.append("=" * 70)
        return "\n".join(lines)
