"""
Result Exporter - 결과 내보내기 및 비교 모듈

통합 테스트 결과를 JSON 파일로 내보내고, 이전 결과와 비교하는 기능을 제공합니다.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Any

from .integration_runner import IntegrationResult, ExecutionLog, ExecutionError, ExecutionStage


@dataclass
class ComparisonResult:
    """결과 비교 정보"""
    is_identical: bool
    differences: list[str]
    summary: str


class ResultExporter:
    """통합 테스트 결과 내보내기 및 비교"""

    def __init__(self):
        pass

    def export_to_json(
        self,
        result: IntegrationResult,
        output_path: str | Path,
        metadata: Optional[dict] = None
    ) -> Path:
        """
        통합 테스트 결과를 JSON 파일로 내보냅니다.

        Args:
            result: 통합 테스트 결과
            output_path: 출력 파일 경로
            metadata: 추가 메타데이터

        Returns:
            Path: 저장된 파일 경로
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "success": result.success,
            "logs": self._serialize_logs(result.logs),
            "errors": self._serialize_errors(result.errors),
            "final_state": self._serialize_state(result.final_state),
            "intermediate_values": result.intermediate_values
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        return output_path

    def _serialize_logs(self, logs: list[ExecutionLog]) -> list[dict]:
        """실행 로그를 직렬화합니다."""
        serialized = []
        for log in logs:
            entry = {
                "stage": log.stage.value,
                "script_name": log.script_name,
                "success": log.success,
                "duration_ms": log.duration_ms,
                "inputs": self._serialize_state(log.inputs),
                "outputs": self._serialize_state(log.outputs),
            }
            if log.error:
                entry["error"] = {
                    "stage": log.error.stage.value,
                    "script_name": log.error.script_name,
                    "line": log.error.line,
                    "error_type": log.error.error_type,
                    "message": log.error.message,
                }
            serialized.append(entry)
        return serialized

    def _serialize_errors(self, errors: list[ExecutionError]) -> list[dict]:
        """오류 목록을 직렬화합니다."""
        return [
            {
                "stage": err.stage.value,
                "script_name": err.script_name,
                "line": err.line,
                "error_type": err.error_type,
                "message": err.message,
            }
            for err in errors
        ]

    def _serialize_state(self, state: dict) -> dict:
        """상태를 직렬화합니다."""
        serialized = {}
        for key, value in state.items():
            if hasattr(value, "__dict__"):
                serialized[key] = self._serialize_object(value)
            elif isinstance(value, dict):
                serialized[key] = self._serialize_state(value)
            else:
                serialized[key] = value
        return serialized

    def _serialize_object(self, obj: Any) -> dict:
        """객체를 직렬화합니다."""
        if hasattr(obj, "value"):
            return {
                "name": getattr(obj, "name", ""),
                "value": obj.value,
                "unit": getattr(obj, "unit", ""),
            }
        elif hasattr(obj, "__dict__"):
            return {k: self._serialize_object(v) if hasattr(v, "__dict__") else v
                    for k, v in obj.__dict__.items() if not k.startswith("_")}
        return str(obj)

    def load_from_json(self, file_path: str | Path) -> dict:
        """
        JSON 파일에서 결과를 로드합니다.

        Args:
            file_path: JSON 파일 경로

        Returns:
            dict: 로드된 결과 데이터
        """
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def compare_results(
        self,
        result1: dict | IntegrationResult,
        result2: dict | IntegrationResult,
        tolerance: float = 1e-6
    ) -> ComparisonResult:
        """
        두 결과를 비교합니다.

        Args:
            result1: 첫 번째 결과 (dict 또는 IntegrationResult)
            result2: 두 번째 결과
            tolerance: 숫자 비교 허용 오차

        Returns:
            ComparisonResult: 비교 결과
        """
        # IntegrationResult인 경우 dict로 변환
        if isinstance(result1, IntegrationResult):
            result1 = {"success": result1.success, "final_state": result1.final_state}
        if isinstance(result2, IntegrationResult):
            result2 = {"success": result2.success, "final_state": result2.final_state}

        differences = []

        # success 비교
        if result1.get("success") != result2.get("success"):
            differences.append(f"success: {result1.get('success')} vs {result2.get('success')}")

        # final_state 비교
        state_diffs = self._compare_states(
            result1.get("final_state", {}),
            result2.get("final_state", {}),
            tolerance,
            "final_state"
        )
        differences.extend(state_diffs)

        is_identical = len(differences) == 0
        summary = "결과가 동일합니다." if is_identical else f"{len(differences)}개의 차이점 발견"

        return ComparisonResult(
            is_identical=is_identical,
            differences=differences,
            summary=summary
        )

    def _compare_states(
        self,
        state1: dict,
        state2: dict,
        tolerance: float,
        path: str
    ) -> list[str]:
        """두 상태를 재귀적으로 비교합니다."""
        differences = []

        all_keys = set(state1.keys()) | set(state2.keys())

        for key in all_keys:
            current_path = f"{path}.{key}"

            if key not in state1:
                differences.append(f"{current_path}: result1에 없음")
                continue
            if key not in state2:
                differences.append(f"{current_path}: result2에 없음")
                continue

            val1 = state1[key]
            val2 = state2[key]

            if isinstance(val1, dict) and isinstance(val2, dict):
                differences.extend(self._compare_states(val1, val2, tolerance, current_path))
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if abs(val1 - val2) > tolerance:
                    differences.append(f"{current_path}: {val1} vs {val2}")
            elif val1 != val2:
                differences.append(f"{current_path}: {val1} vs {val2}")

        return differences

    def generate_comparison_report(
        self,
        comparison: ComparisonResult,
        result1_name: str = "Result 1",
        result2_name: str = "Result 2"
    ) -> str:
        """
        비교 결과 리포트를 생성합니다.

        Args:
            comparison: 비교 결과
            result1_name: 첫 번째 결과 이름
            result2_name: 두 번째 결과 이름

        Returns:
            str: 리포트 문자열
        """
        lines = [
            "=" * 70,
            "결과 비교 리포트",
            "=" * 70,
            f"비교 대상: {result1_name} vs {result2_name}",
            f"결과: {comparison.summary}",
            ""
        ]

        if comparison.differences:
            lines.append("차이점:")
            for diff in comparison.differences:
                lines.append(f"  - {diff}")
        else:
            lines.append("모든 값이 일치합니다.")

        lines.append("=" * 70)
        return "\n".join(lines)
