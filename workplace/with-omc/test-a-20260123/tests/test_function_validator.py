"""FunctionValidator 테스트"""

import pytest
from formula_checker.function_validator import FunctionValidator, FormulaType


class TestFunctionValidator:
    """FunctionValidator 테스트 클래스"""

    def setup_method(self):
        self.validator = FunctionValidator()

    def test_structure_all_functions(self):
        """Structure 계산식 - 모든 필수 함수 정의됨"""
        source = """
def forward_calculate(DSP, result):
    return result

def reverse_calculate(DSP, forward_result):
    return True

def level_calculate(DSP, forward_result, result, drawing):
    return (result, drawing)
"""
        result = self.validator.validate_source(source, "structure.py", FormulaType.STRUCTURE)
        assert result.is_valid
        assert len(result.missing_functions) == 0
        assert len(result.found_functions) == 3

    def test_structure_missing_function(self):
        """Structure 계산식 - 함수 누락"""
        source = """
def forward_calculate(DSP, result):
    return result

def reverse_calculate(DSP, forward_result):
    return True
# level_calculate 누락
"""
        result = self.validator.validate_source(source, "structure.py", FormulaType.STRUCTURE)
        assert not result.is_valid
        assert "level_calculate" in result.missing_functions

    def test_equipment_function(self):
        """Equipment 계산식 - forward_calculate만 필요"""
        source = """
def forward_calculate(DEP, result):
    result.power = 100
    return result
"""
        result = self.validator.validate_source(source, "equipment.py", FormulaType.EQUIPMENT)
        assert result.is_valid

    def test_process_no_requirement(self):
        """Process 계산식 - 필수 함수 없음"""
        source = """
from WAI import DCN, SingleValue

DCN.influents.q = SingleValue("Q", 100, False, "m³/d")
"""
        result = self.validator.validate_source(source, "process.py", FormulaType.PROCESS)
        assert result.is_valid

    def test_detect_structure_type(self):
        """계산식 타입 자동 감지 - Structure"""
        source = """
def forward_calculate(): pass
def reverse_calculate(): pass
def level_calculate(): pass
"""
        detected = self.validator.detect_formula_type(source)
        assert detected == FormulaType.STRUCTURE

    def test_detect_equipment_type(self):
        """계산식 타입 자동 감지 - Equipment"""
        source = """
def forward_calculate():
    return {}
"""
        detected = self.validator.detect_formula_type(source)
        assert detected == FormulaType.EQUIPMENT

    def test_detect_process_type(self):
        """계산식 타입 자동 감지 - Process"""
        source = """
from WAI import DCN, DCP
DCN.influents.q = 100
"""
        detected = self.validator.detect_formula_type(source)
        assert detected == FormulaType.PROCESS
