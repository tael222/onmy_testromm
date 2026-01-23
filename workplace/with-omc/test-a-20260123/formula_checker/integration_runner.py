"""
Integration Runner - exec 기반 조합 실행 모듈

공정 계산식 내에서 구조물/기계 계산식을 exec()로 실행하는 구조를 재현합니다.
"""

import sys
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import copy


class ExecutionStage(Enum):
    """실행 단계"""
    PROCESS = "process"
    STRUCTURE_FORWARD = "structure_forward"
    STRUCTURE_REVERSE = "structure_reverse"
    STRUCTURE_LEVEL = "structure_level"
    EQUIPMENT_FORWARD = "equipment_forward"


@dataclass
class ExecutionError:
    """실행 오류 정보"""
    stage: ExecutionStage
    script_name: str
    line: Optional[int]
    error_type: str
    message: str
    traceback: str


@dataclass
class ExecutionLog:
    """실행 로그"""
    stage: ExecutionStage
    script_name: str
    success: bool
    duration_ms: float
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    error: Optional[ExecutionError] = None


@dataclass
class IntegrationResult:
    """통합 테스트 결과"""
    success: bool
    logs: list[ExecutionLog]
    final_state: dict
    errors: list[ExecutionError]
    intermediate_values: dict = field(default_factory=dict)


class MockWAIModule:
    """테스트용 WAI 모듈 Mock"""

    def __init__(self, instance_id: str = "test"):
        self.instance_id = instance_id
        self._containers = {
            "DCN": self._create_container(),
            "DCR": self._create_container(),
            "DCP": self._create_container(),
            "DSP": self._create_container(),
            "DEP": self._create_container(),
            "STC": self._create_container(),
            "EQP": self._create_container(),
            "STD": self._create_container(),
            "INF": self._create_container(),
            "HWL": self._create_container(),
            "OPX": self._create_container(),
            "MAP": self._create_container(),
            "GV": self._create_container(),
        }

    def _create_container(self) -> "DotDict":
        return DotDict()

    def get_container(self, name: str) -> "DotDict":
        return self._containers.get(name, DotDict())

    def get_all_containers(self) -> dict:
        return copy.deepcopy(self._containers)


class DotDict(dict):
    """점 표기법을 지원하는 딕셔너리"""

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_"):
            return super().__getattribute__(key)
        if key not in self:
            self[key] = DotDict()
        return self[key]

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key: str) -> None:
        if key in self:
            del self[key]


class SingleValue:
    """Mock SingleValue"""
    def __init__(self, name: str, value: float = 0, editable: bool = True,
                 unit: str = "", remark: str = "", **kwargs):
        self.name = name
        self._value = value
        self.editable = editable
        self.unit = unit
        self.remark = remark
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        self._value = v

    def __repr__(self) -> str:
        return f"SingleValue({self.name}={self._value} {self.unit})"


class RangedValue(SingleValue):
    """Mock RangedValue"""
    def __init__(self, name: str, value: float = 0, editable: bool = True,
                 Min: float = 0, Max: float = 0, unit: str = "", **kwargs):
        super().__init__(name, value, editable, unit, **kwargs)
        self.Min = Min
        self.Max = Max


class IntegrationRunner:
    """exec 기반 통합 테스트를 실행하는 클래스"""

    def __init__(self, instance_id: str = "test"):
        self.instance_id = instance_id
        self.wai = MockWAIModule(instance_id)
        self._logs: list[ExecutionLog] = []
        self._errors: list[ExecutionError] = []
        self._intermediate_values: dict = {}

    def _build_globals(self) -> dict:
        """exec 실행을 위한 전역 네임스페이스 구성"""
        return {
            "__builtins__": __builtins__,
            "DCN": self.wai.get_container("DCN"),
            "DCR": self.wai.get_container("DCR"),
            "DCP": self.wai.get_container("DCP"),
            "DSP": self.wai.get_container("DSP"),
            "DEP": self.wai.get_container("DEP"),
            "STC": self.wai.get_container("STC"),
            "EQP": self.wai.get_container("EQP"),
            "STD": self.wai.get_container("STD"),
            "INF": self.wai.get_container("INF"),
            "HWL": self.wai.get_container("HWL"),
            "OPX": self.wai.get_container("OPX"),
            "MAP": self.wai.get_container("MAP"),
            "GV": self.wai.get_container("GV"),
            "SingleValue": SingleValue,
            "RangedValue": RangedValue,
            "DotDict": DotDict,
        }

    def run_process(self, process_script: str, script_name: str = "process.py") -> ExecutionLog:
        """
        공정 계산식을 실행합니다.

        Args:
            process_script: 공정 계산식 소스 코드
            script_name: 스크립트 이름

        Returns:
            ExecutionLog: 실행 로그
        """
        import time
        start = time.perf_counter()

        globals_dict = self._build_globals()
        locals_dict = {}

        try:
            exec(process_script, globals_dict, locals_dict)

            duration = (time.perf_counter() - start) * 1000
            log = ExecutionLog(
                stage=ExecutionStage.PROCESS,
                script_name=script_name,
                success=True,
                duration_ms=duration,
                outputs=self._extract_outputs()
            )
            self._logs.append(log)
            return log

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            tb = traceback.format_exc()

            # 오류 라인 추출
            line_no = None
            for line in tb.split("\n"):
                if script_name in line:
                    try:
                        line_no = int(line.split("line")[1].split(",")[0].strip())
                    except (IndexError, ValueError):
                        pass

            error = ExecutionError(
                stage=ExecutionStage.PROCESS,
                script_name=script_name,
                line=line_no,
                error_type=type(e).__name__,
                message=str(e),
                traceback=tb
            )
            self._errors.append(error)

            log = ExecutionLog(
                stage=ExecutionStage.PROCESS,
                script_name=script_name,
                success=False,
                duration_ms=duration,
                error=error
            )
            self._logs.append(log)
            return log

    def run_structure_script(
        self,
        script: str,
        stage: ExecutionStage,
        script_name: str,
        inputs: Optional[dict] = None
    ) -> ExecutionLog:
        """
        구조물 계산식을 실행합니다.

        Args:
            script: 구조물 계산식 소스 코드
            stage: 실행 단계
            script_name: 스크립트 이름
            inputs: 입력 파라미터

        Returns:
            ExecutionLog: 실행 로그
        """
        import time
        start = time.perf_counter()

        globals_dict = self._build_globals()
        if inputs:
            globals_dict.update(inputs)

        locals_dict = {}

        try:
            exec(script, globals_dict, locals_dict)

            # 함수 호출
            func_name = {
                ExecutionStage.STRUCTURE_FORWARD: "forward_calculate",
                ExecutionStage.STRUCTURE_REVERSE: "reverse_calculate",
                ExecutionStage.STRUCTURE_LEVEL: "level_calculate",
            }.get(stage)

            result = None
            if func_name and func_name in locals_dict:
                func = locals_dict[func_name]
                result = func()

            duration = (time.perf_counter() - start) * 1000
            log = ExecutionLog(
                stage=stage,
                script_name=script_name,
                success=True,
                duration_ms=duration,
                inputs=inputs or {},
                outputs={"result": result} if result else {}
            )
            self._logs.append(log)
            return log

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            tb = traceback.format_exc()

            error = ExecutionError(
                stage=stage,
                script_name=script_name,
                line=None,
                error_type=type(e).__name__,
                message=str(e),
                traceback=tb
            )
            self._errors.append(error)

            log = ExecutionLog(
                stage=stage,
                script_name=script_name,
                success=False,
                duration_ms=duration,
                inputs=inputs or {},
                error=error
            )
            self._logs.append(log)
            return log

    def run_equipment_script(
        self,
        script: str,
        script_name: str,
        inputs: Optional[dict] = None
    ) -> ExecutionLog:
        """
        기계설비 계산식을 실행합니다.

        Args:
            script: 기계설비 계산식 소스 코드
            script_name: 스크립트 이름
            inputs: 입력 파라미터

        Returns:
            ExecutionLog: 실행 로그
        """
        import time
        start = time.perf_counter()

        globals_dict = self._build_globals()
        if inputs:
            globals_dict.update(inputs)

        locals_dict = {}

        try:
            exec(script, globals_dict, locals_dict)

            result = None
            if "forward_calculate" in locals_dict:
                result = locals_dict["forward_calculate"]()

            duration = (time.perf_counter() - start) * 1000
            log = ExecutionLog(
                stage=ExecutionStage.EQUIPMENT_FORWARD,
                script_name=script_name,
                success=True,
                duration_ms=duration,
                inputs=inputs or {},
                outputs={"result": result} if result else {}
            )
            self._logs.append(log)
            return log

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            tb = traceback.format_exc()

            error = ExecutionError(
                stage=ExecutionStage.EQUIPMENT_FORWARD,
                script_name=script_name,
                line=None,
                error_type=type(e).__name__,
                message=str(e),
                traceback=tb
            )
            self._errors.append(error)

            log = ExecutionLog(
                stage=ExecutionStage.EQUIPMENT_FORWARD,
                script_name=script_name,
                success=False,
                duration_ms=duration,
                inputs=inputs or {},
                error=error
            )
            self._logs.append(log)
            return log

    def run_integration_test(
        self,
        process_script: str,
        structure_scripts: Optional[dict[str, str]] = None,
        equipment_scripts: Optional[dict[str, str]] = None
    ) -> IntegrationResult:
        """
        전체 통합 테스트를 실행합니다.

        Args:
            process_script: 공정 계산식
            structure_scripts: {이름: 소스코드} 형태의 구조물 계산식들
            equipment_scripts: {이름: 소스코드} 형태의 기계설비 계산식들

        Returns:
            IntegrationResult: 통합 테스트 결과
        """
        self._logs = []
        self._errors = []

        # 1. 공정 계산식 실행
        self.run_process(process_script)

        # 2. 구조물 계산식 실행
        if structure_scripts:
            for name, script in structure_scripts.items():
                for stage in [
                    ExecutionStage.STRUCTURE_FORWARD,
                    ExecutionStage.STRUCTURE_REVERSE,
                    ExecutionStage.STRUCTURE_LEVEL
                ]:
                    self.run_structure_script(script, stage, name)

        # 3. 기계설비 계산식 실행
        if equipment_scripts:
            for name, script in equipment_scripts.items():
                self.run_equipment_script(script, name)

        success = all(log.success for log in self._logs)

        return IntegrationResult(
            success=success,
            logs=self._logs,
            final_state=self._extract_outputs(),
            errors=self._errors,
            intermediate_values=self._intermediate_values
        )

    def _extract_outputs(self) -> dict:
        """현재 컨테이너 상태를 추출합니다."""
        outputs = {}
        for name, container in self.wai._containers.items():
            if container:
                outputs[name] = dict(container)
        return outputs

    def capture_intermediate(self, name: str, value: Any) -> None:
        """중간값을 캡처합니다."""
        self._intermediate_values[name] = value

    def get_logs(self) -> list[ExecutionLog]:
        """실행 로그를 반환합니다."""
        return self._logs

    def get_errors(self) -> list[ExecutionError]:
        """오류 목록을 반환합니다."""
        return self._errors
