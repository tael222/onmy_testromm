"""IntegrationRunner 테스트"""

import pytest
from formula_checker.integration_runner import IntegrationRunner, ExecutionStage


class TestIntegrationRunner:
    """IntegrationRunner 테스트 클래스"""

    def setup_method(self):
        self.runner = IntegrationRunner()

    def test_simple_process_execution(self):
        """간단한 공정 계산식 실행"""
        process_script = """
DCN.influents.q = SingleValue("Q", 579.5, False, "m³/d")
DCN.influents.bod = SingleValue("BOD", 207.0, False, "mg/L")
"""
        log = self.runner.run_process(process_script, "simple_process.py")

        assert log.success
        assert log.stage == ExecutionStage.PROCESS
        assert log.duration_ms >= 0

    def test_process_with_calculation(self):
        """계산이 포함된 공정 계산식 실행"""
        process_script = """
DCN.influents.q = SingleValue("Q", 579.5, False, "m³/d")
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")
DSP.tank.volume.value = DCN.influents.q.value * 6 / 24  # HRT 6시간
"""
        log = self.runner.run_process(process_script, "calc_process.py")

        assert log.success
        # 결과 확인
        outputs = log.outputs
        assert "DSP" in outputs

    def test_process_with_syntax_error(self):
        """문법 오류가 있는 공정 계산식"""
        process_script = """
DCN.influents.q = SingleValue("Q", 579.5, False  # 괄호 누락
"""
        log = self.runner.run_process(process_script, "error_process.py")

        assert not log.success
        assert log.error is not None
        assert log.error.error_type == "SyntaxError"

    def test_process_with_runtime_error(self):
        """런타임 오류가 있는 공정 계산식"""
        process_script = """
result = 1 / 0  # ZeroDivisionError
"""
        log = self.runner.run_process(process_script, "runtime_error.py")

        assert not log.success
        assert log.error is not None
        assert log.error.error_type == "ZeroDivisionError"

    def test_equipment_script_execution(self):
        """기계설비 계산식 실행"""
        equipment_script = """
def forward_calculate():
    result = DotDict()
    result.power = SingleValue("power", 100, False, unit="kW")
    return result
"""
        log = self.runner.run_equipment_script(
            equipment_script,
            "pump.py"
        )

        assert log.success
        assert log.stage == ExecutionStage.EQUIPMENT_FORWARD

    def test_integration_test_success(self):
        """통합 테스트 성공 케이스"""
        process_script = """
DCN.influents.q = SingleValue("Q", 100, False, "m³/d")
DSP.tank.volume = SingleValue("Volume", 25, False, unit="m³")
"""
        result = self.runner.run_integration_test(process_script)

        assert result.success
        assert len(result.logs) == 1
        assert len(result.errors) == 0

    def test_integration_test_with_equipment(self):
        """기계설비 포함 통합 테스트"""
        process_script = """
DCN.influents.q = SingleValue("Q", 100, False, "m³/d")
"""
        equipment_scripts = {
            "pump": """
def forward_calculate():
    result = DotDict()
    result.capacity = SingleValue("capacity", 50, False, unit="m³/d")
    return result
"""
        }

        result = self.runner.run_integration_test(
            process_script,
            equipment_scripts=equipment_scripts
        )

        assert result.success
        assert len(result.logs) == 2  # process + equipment

    def test_container_isolation(self):
        """컨테이너 격리 테스트"""
        # 첫 번째 실행
        runner1 = IntegrationRunner("instance_1")
        runner1.run_process("""
DCN.influents.q = SingleValue("Q", 100, False, "m³/d")
""")

        # 두 번째 실행 (별도 인스턴스)
        runner2 = IntegrationRunner("instance_2")
        runner2.run_process("""
DCN.influents.q = SingleValue("Q", 200, False, "m³/d")
""")

        # 각각 독립적인 값을 가져야 함
        state1 = runner1.wai.get_container("DCN")
        state2 = runner2.wai.get_container("DCN")

        assert state1.influents.q.value == 100
        assert state2.influents.q.value == 200
