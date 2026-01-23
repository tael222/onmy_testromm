"""
CLI - 명령줄 인터페이스

Formula Checker의 명령줄 인터페이스를 제공합니다.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .syntax_checker import SyntaxChecker
from .function_validator import FunctionValidator, FormulaType
from .container_validator import ContainerValidator
from .integration_runner import IntegrationRunner
from .input_controller import InputController
from .result_exporter import ResultExporter


def check_syntax(args: argparse.Namespace) -> int:
    """문법 검사 명령"""
    checker = SyntaxChecker()

    if args.directory:
        results = checker.check_directory(args.path)
    else:
        results = [checker.check_file(args.path)]

    has_errors = False

    for result in results:
        if result.is_valid:
            print(f"✓ {result.file_path}: 문법 오류 없음")
        else:
            has_errors = True
            print(f"✗ {result.file_path}: 문법 오류 발견")
            for error in result.errors:
                print(f"  Line {error.line}, Col {error.column}: {error.message}")
                if error.code_snippet:
                    print(f"    > {error.code_snippet}")

    return 1 if has_errors else 0


def validate_functions(args: argparse.Namespace) -> int:
    """함수 검증 명령"""
    validator = FunctionValidator()

    try:
        formula_type = FormulaType(args.type)
    except ValueError:
        print(f"오류: 알 수 없는 계산식 타입 '{args.type}'")
        print(f"허용되는 타입: {', '.join(t.value for t in FormulaType)}")
        return 1

    result = validator.validate_file(args.path, formula_type)

    if result.is_valid:
        print(f"✓ {result.file_path}: 필수 함수 정의됨")
        print(f"  발견된 함수:")
        for func in result.found_functions:
            sig = validator.get_function_signature(func)
            print(f"    - {sig} (line {func.line})")
    else:
        print(f"✗ {result.file_path}: 필수 함수 누락")
        print(f"  누락된 함수: {', '.join(result.missing_functions)}")
        print(f"  발견된 함수:")
        for func in result.found_functions:
            print(f"    - {func.name} (line {func.line})")

    return 0 if result.is_valid else 1


def validate_containers(args: argparse.Namespace) -> int:
    """컨테이너 검증 명령"""
    validator = ContainerValidator()
    result = validator.validate_file(args.path)

    if result.is_valid:
        print(f"✓ {result.file_path}: 컨테이너 사용 적합")
    else:
        print(f"✗ {result.file_path}: 컨테이너 사용 오류")

    if result.errors:
        print("  오류:")
        for error in result.errors:
            print(f"    - {error}")

    if result.warnings:
        print("  경고:")
        for warning in result.warnings:
            print(f"    - {warning}")

    if args.verbose and result.usages:
        print("  컨테이너 사용 현황:")
        for usage in result.usages:
            status = "✓" if usage.is_valid else "✗"
            type_str = usage.value_type or "(재할당)"
            print(f"    {status} {usage.container.value}.{usage.attribute_path} = {type_str} (line {usage.line})")

    return 0 if result.is_valid else 1


def run_integration(args: argparse.Namespace) -> int:
    """통합 테스트 명령"""
    process_path = Path(args.process)

    if not process_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {process_path}")
        return 1

    process_script = process_path.read_text(encoding="utf-8")

    structure_scripts = {}
    if args.structures:
        for s_path in args.structures:
            p = Path(s_path)
            if p.exists():
                structure_scripts[p.stem] = p.read_text(encoding="utf-8")

    equipment_scripts = {}
    if args.equipments:
        for e_path in args.equipments:
            p = Path(e_path)
            if p.exists():
                equipment_scripts[p.stem] = p.read_text(encoding="utf-8")

    runner = IntegrationRunner()

    # 입력값 적용
    if args.inputs:
        controller = InputController()
        test_case = controller.load_test_case(args.inputs)
        controller._inputs = test_case.inputs
        controller.apply_inputs_to_runner(runner)

    result = runner.run_integration_test(
        process_script,
        structure_scripts or None,
        equipment_scripts or None
    )

    print("=" * 60)
    print(f"통합 테스트 결과: {'성공' if result.success else '실패'}")
    print("=" * 60)

    print("\n실행 로그:")
    for log in result.logs:
        status = "✓" if log.success else "✗"
        print(f"  {status} [{log.stage.value}] {log.script_name} ({log.duration_ms:.2f}ms)")
        if log.error:
            print(f"      오류: {log.error.error_type}: {log.error.message}")

    if result.errors:
        print("\n오류 상세:")
        for error in result.errors:
            print(f"\n  [{error.stage.value}] {error.script_name}")
            print(f"  타입: {error.error_type}")
            print(f"  메시지: {error.message}")
            if error.line:
                print(f"  라인: {error.line}")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "success": result.success,
                "logs": [
                    {
                        "stage": log.stage.value,
                        "script_name": log.script_name,
                        "success": log.success,
                        "duration_ms": log.duration_ms,
                    }
                    for log in result.logs
                ],
                "errors": [
                    {
                        "stage": err.stage.value,
                        "script_name": err.script_name,
                        "error_type": err.error_type,
                        "message": err.message,
                    }
                    for err in result.errors
                ],
            }, f, ensure_ascii=False, indent=2)
        print(f"\n결과가 저장됨: {output_path}")

    return 0 if result.success else 1


def check_all(args: argparse.Namespace) -> int:
    """전체 검사 명령 (문법 + 함수 + 컨테이너)"""
    path = Path(args.path)

    if not path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {path}")
        return 1

    source_code = path.read_text(encoding="utf-8")
    has_errors = False

    print(f"\n{'=' * 60}")
    print(f"전체 검사: {path}")
    print("=" * 60)

    # 1. 문법 검사
    print("\n[1/3] 문법 검사...")
    syntax_checker = SyntaxChecker()
    syntax_result = syntax_checker.check_file(path)

    if syntax_result.is_valid:
        print("  ✓ 문법 오류 없음")
    else:
        has_errors = True
        print("  ✗ 문법 오류 발견")
        for error in syntax_result.errors:
            print(f"    Line {error.line}: {error.message}")

    # 2. 함수 검증
    print("\n[2/3] 함수 검증...")
    func_validator = FunctionValidator()
    detected_type = func_validator.detect_formula_type(source_code)

    if detected_type:
        print(f"  계산식 타입: {detected_type.value}")
        func_result = func_validator.validate_source(source_code, str(path), detected_type)

        if func_result.is_valid:
            print("  ✓ 필수 함수 정의됨")
        else:
            has_errors = True
            print(f"  ✗ 누락된 함수: {', '.join(func_result.missing_functions)}")
    else:
        print("  계산식 타입을 자동 감지할 수 없습니다.")

    # 3. 컨테이너 검증
    print("\n[3/3] 컨테이너 검증...")
    container_validator = ContainerValidator()
    container_result = container_validator.validate_file(path)

    if container_result.is_valid:
        print("  ✓ 컨테이너 사용 적합")
    else:
        has_errors = True
        print("  ✗ 컨테이너 사용 오류")
        for error in container_result.errors:
            print(f"    {error}")

    if container_result.warnings:
        print("  경고:")
        for warning in container_result.warnings:
            print(f"    {warning}")

    print(f"\n{'=' * 60}")
    print(f"결과: {'모든 검사 통과' if not has_errors else '일부 검사 실패'}")
    print("=" * 60)

    return 1 if has_errors else 0


def compare_results(args: argparse.Namespace) -> int:
    """결과 비교 명령"""
    exporter = ResultExporter()

    result1_path = Path(args.file1)
    result2_path = Path(args.file2)

    if not result1_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {result1_path}")
        return 1
    if not result2_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {result2_path}")
        return 1

    result1 = exporter.load_from_json(result1_path)
    result2 = exporter.load_from_json(result2_path)

    comparison = exporter.compare_results(result1, result2, tolerance=args.tolerance)
    report = exporter.generate_comparison_report(
        comparison,
        result1_name=result1_path.name,
        result2_name=result2_path.name
    )

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"\n리포트 저장됨: {output_path}")

    return 0 if comparison.is_identical else 1


def main(argv: Optional[list[str]] = None) -> int:
    """메인 진입점"""
    parser = argparse.ArgumentParser(
        prog="formula-checker",
        description="WAI 계산식 검증 도구"
    )

    subparsers = parser.add_subparsers(dest="command", help="명령")

    # syntax 명령
    syntax_parser = subparsers.add_parser("syntax", help="문법 검사")
    syntax_parser.add_argument("path", help="검사할 파일 또는 디렉토리 경로")
    syntax_parser.add_argument("-d", "--directory", action="store_true",
                               help="디렉토리 내 모든 .py 파일 검사")

    # function 명령
    func_parser = subparsers.add_parser("function", help="함수 정의 검증")
    func_parser.add_argument("path", help="검사할 파일 경로")
    func_parser.add_argument("-t", "--type", required=True,
                             choices=["process", "structure", "equipment"],
                             help="계산식 타입")

    # container 명령
    container_parser = subparsers.add_parser("container", help="컨테이너 사용 검증")
    container_parser.add_argument("path", help="검사할 파일 경로")
    container_parser.add_argument("-v", "--verbose", action="store_true",
                                  help="상세 정보 출력")

    # integration 명령
    integration_parser = subparsers.add_parser("integration", help="통합 테스트 실행")
    integration_parser.add_argument("process", help="공정 계산식 파일 경로")
    integration_parser.add_argument("-s", "--structures", nargs="*",
                                    help="구조물 계산식 파일 경로들")
    integration_parser.add_argument("-e", "--equipments", nargs="*",
                                    help="기계설비 계산식 파일 경로들")
    integration_parser.add_argument("-i", "--inputs", help="입력값 JSON 파일 경로")
    integration_parser.add_argument("-o", "--output", help="결과 출력 JSON 파일 경로")

    # check 명령 (전체 검사)
    check_parser = subparsers.add_parser("check", help="전체 검사 (문법+함수+컨테이너)")
    check_parser.add_argument("path", help="검사할 파일 경로")

    # compare 명령 (결과 비교)
    compare_parser = subparsers.add_parser("compare", help="두 결과 파일 비교")
    compare_parser.add_argument("file1", help="첫 번째 결과 JSON 파일")
    compare_parser.add_argument("file2", help="두 번째 결과 JSON 파일")
    compare_parser.add_argument("-t", "--tolerance", type=float, default=1e-6,
                                help="숫자 비교 허용 오차 (기본값: 1e-6)")
    compare_parser.add_argument("-o", "--output", help="비교 리포트 출력 파일 경로")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "syntax": check_syntax,
        "function": validate_functions,
        "container": validate_containers,
        "integration": run_integration,
        "check": check_all,
        "compare": compare_results,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
