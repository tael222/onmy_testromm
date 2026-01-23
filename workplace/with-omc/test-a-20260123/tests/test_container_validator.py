"""ContainerValidator 테스트"""

import pytest
from formula_checker.container_validator import ContainerValidator, ContainerType, ValueObjectType


class TestContainerValidator:
    """ContainerValidator 테스트 클래스"""

    def setup_method(self):
        self.validator = ContainerValidator()

    def test_valid_dcn_usage(self):
        """DCN 컨테이너 올바른 사용"""
        source = """
from WAI import DCN, SingleValue, RangedValue

DCN.influents.q = SingleValue("Q", 579.5, False, "m³/d")
DCN.efficiency.bod = RangedValue("BOD", 95, True, 90, 98, unit="%")
"""
        result = self.validator.validate_source(source, "test.py")
        assert result.is_valid

    def test_valid_stc_usage(self):
        """STC 컨테이너 올바른 사용"""
        source = """
from WAI import STC, StructureValue

STC.tank = StructureValue(name="탱크", code_key="CONCRETE_SQUARE")
"""
        result = self.validator.validate_source(source, "test.py")
        assert result.is_valid

    def test_invalid_stc_usage(self):
        """STC 컨테이너 잘못된 사용 (SingleValue 할당)"""
        source = """
from WAI import STC, SingleValue

STC.tank = SingleValue("탱크", 100)  # STC에는 StructureValue만 허용
"""
        result = self.validator.validate_source(source, "test.py")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_reassignment_pattern(self):
        """재할당 패턴 검증"""
        source = """
from WAI import DSP, SingleValue

# 올바른 패턴: 먼저 SingleValue로 선언
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")
# 그 다음 값 재할당
DSP.tank.volume = calculated_value
"""
        result = self.validator.validate_source(source, "test.py")
        # 첫 번째 할당이 SingleValue이므로 경고 없음
        assert len(result.warnings) == 0

    def test_multiple_containers(self):
        """여러 컨테이너 동시 사용"""
        source = """
from WAI import DCN, DCP, DSP, SingleValue, RangedValue

DCN.influents.q = SingleValue("Q", 100, unit="m³/d")
DCP.HRT.value = RangedValue("HRT", 6, True, 3, 24, unit="h")
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")
"""
        result = self.validator.validate_source(source, "test.py")
        assert result.is_valid
        assert len(result.usages) == 3

    def test_nested_attributes(self):
        """중첩 속성 사용"""
        source = """
from WAI import DCN, SingleValue

DCN.effluents.water.q = SingleValue("Q", 100)
DCN.effluents.water.bod = SingleValue("BOD", 200)
"""
        result = self.validator.validate_source(source, "test.py")
        assert result.is_valid
        assert len(result.usages) == 2
