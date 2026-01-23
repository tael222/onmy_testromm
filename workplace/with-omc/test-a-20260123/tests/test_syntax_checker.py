"""SyntaxChecker 테스트"""

import pytest
from formula_checker.syntax_checker import SyntaxChecker


class TestSyntaxChecker:
    """SyntaxChecker 테스트 클래스"""

    def setup_method(self):
        self.checker = SyntaxChecker()

    def test_valid_syntax(self):
        """유효한 Python 문법 검사"""
        source = """
def calculate(x, y):
    return x + y

result = calculate(1, 2)
"""
        result = self.checker.check_source(source, "test.py")
        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_syntax(self):
        """무효한 Python 문법 검사"""
        source = """
def calculate(x, y)  # missing colon
    return x + y
"""
        result = self.checker.check_source(source, "test.py")
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.errors[0].line == 2

    def test_indentation_error(self):
        """들여쓰기 오류 검사"""
        source = """
def calculate():
return 1  # wrong indentation
"""
        result = self.checker.check_source(source, "test.py")
        assert not result.is_valid

    def test_empty_source(self):
        """빈 소스 코드 검사"""
        result = self.checker.check_source("", "test.py")
        assert result.is_valid

    def test_wai_style_code(self):
        """WAI 스타일 코드 검사"""
        source = """
from WAI import DCN, SingleValue

DCN.influents.q = SingleValue("Q", 579.5, False, "m³/d")
DCN.influents.bod = SingleValue("BOD", 207.0, False, "mg/L")
"""
        result = self.checker.check_source(source, "process.py")
        assert result.is_valid
