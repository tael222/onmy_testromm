# WAI: Unity-Python Integration Module

WAI는 Unity와 Python을 통해 연결하기 위한 **설계 계산용 내장 모듈**입니다.
각 인스턴스에 대한 데이터 스코프를 관리하고, 설계 입력값, 기준, 결과 등을 다루는 구조로 설계되어 있습니다.

## 목차

- [설치 방법](#설치-방법)
- [빠른 시작](#빠른-시작)
- [핵심 개념](#핵심-개념)
- [내부 구조 개요](#내부-구조-개요)
- [주요 컨테이너](#주요-컨테이너)
- [주요 클래스 및 구조](#주요-클래스-및-구조)
- [계산식 작성 가이드](#계산식-작성-가이드)

---

## 설치 방법

```bash
pip install wai-0.1.17-py3-none-any.whl
```

**요구사항**: Python 3.12 이상

---

## 빠른 시작

WAI를 사용한 설계 계산의 기본 흐름입니다.

```python
from WAI import (
    DCN, DCP, DSP, DEP, STC, EQP, INF,
    SingleValue, RangedValue, StructureValue, EquipmentValue,
    Info, UnitSystemType, StructureType
)

# 1. 프로세스 정보 설정
INF.Info = Info(
    process_code="Equalization_Tank",
    unit_system=UnitSystemType.METRIC,
    formula_version="v1.0.0",
    author="홍길동",
    date="2025-10-16"
)

# 2. 설계 조건 입력 (DCN)
DCN.influents.q = SingleValue("Q", 579.5, False, "m³/d")
DCN.influents.bod = SingleValue("BOD", 207.0, False, "mg/L")

# 3. 설계 매개변수 (DSP) - 선언 후 계산값 할당
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")
DSP.tank.volume = DCN.influents.q.value * 6 / 24  # HRT 6시간

# 4. 구조물 정의 (STC) - 생성 후 동적 값 재할당
STC.tank = StructureValue(
    name="유량조정조",
    code_key=StructureType.CONCRETE_SQUARE,
    required_capacity=DSP.tank.volume.value,
    inputs=DSP.tank
)
STC.tank.required_capacity = DSP.tank.volume.value  # 재계산 시 반영
```

> 💡 **전체 예시**: 완전한 공정 계산식 예시는 [계산식 작성 가이드 > Process 계산식 예시](#process-계산식-예시)를 참조하세요.

---

## 핵심 개념

### 인스턴스 스코프 관리

WAI는 **인스턴스별 데이터 분리**를 지원합니다. Unity에서 `setInstanceid(...)` 호출을 통해 개별 오브젝트별로 데이터를 분리 저장합니다.

**동작 방식**:
- Unity에서 각 오브젝트가 생성될 때 자동으로 고유 ID 할당
- 각 오브젝트는 독립적인 설계 데이터 공간 보유
- 스코프를 설정하지 않으면 `"none"`이라는 기본 ID 사용

**예시 시나리오**:
```
Unity 오브젝트 A (ID: "tank_A")
  → DCN.influents.flow = 1000 m³/d

Unity 오브젝트 B (ID: "tank_B")
  → DCN.influents.flow = 2000 m³/d  (A와 독립적)
```

> ⚠️ **주의**: Python 코드에서 `setInstanceid()`를 직접 호출할 필요는 없습니다. Unity에서 자동으로 처리됩니다.

### 재계산 시 동적 값 반영 패턴

WAI는 동일한 Python 파일을 같은 인터프리터 환경에서 **반복 실행**하여 재계산을 수행합니다. 이때 모든 컨테이너에서 **IValueObject 할당은 첫 생성 시에만 적용**되고, 이후 실행에서는 기존 인스턴스가 유지됩니다.

**핵심 원칙**: 동적으로 계산되는 값은 **기본 타입(float, int, str, bool)으로 재할당**해야 재계산 시 변경사항이 반영됩니다.

| 할당 타입 | 키가 없을 때 | 키가 있을 때 |
|----------|-------------|-------------|
| `IValueObject` (SingleValue 등) | 새로 생성 | **무시됨** (기존 값 유지) |
| 기본 타입 (float, int, str, bool) | TypeError | 값 업데이트 |

**올바른 패턴**:
```python
# 1. 선언 (첫 실행 시 생성)
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")

# 2. 재계산 시 동적 값 반영 (float, int 등 기본 타입 사용)
DSP.tank.volume = calculated_value
```

> 💡 각 컨테이너별 상세 패턴은 [주요 컨테이너](#주요-컨테이너) 섹션의 예시를 참조하세요.

### 컨테이너 구조

WAI는 설계 데이터를 **용도별 컨테이너**로 구분하여 관리합니다:

| 컨테이너 | 약어 | 용도 | 주요 사용 시점 | 주요 사용 클래스 |
|---------|------|------|--------------|--------------|
| Design Conditions | DCN | 설계 조건 (유입/유출) | 프로젝트 시작 시 | Single/RangeValue |
| Design Criteria | DCR | 설계 기준 | 설계 기준 정의 시 | Single/RangeValue |
| Design Parameters | DCP | 설계 매개변수 | 공정 계산 시 | Single/Range/Text/Bool/DropboxValue |
| Structure | STC | 구조물 정보 | 구조물 설계 시 | StructureValue |
| Equipment | EQP | 기계설비 정보 | 설비 선정 시 |  EquipmentValue|
| Design Spec Parameters | DSP | 구조물 규격 매개변수 | 구조물 계산식 입력 | Single/Range/Text/Bool/DropboxValue |
| Design Equip Parameters | DEP | 기계설비 매개변수 | 설비 계산식 입력 | Single/Range/Text/Bool/DropboxValue |
| Height Width Length | HWL | 3D 모델링 치수 정보 | 3D 모델링 데이터 전달 시 | SingleValue |
| Operation Expense | OPX | 유지비용 매개변수 | 운영비용 계산 시 | SingleValue |
| Standard | STD | 표준 참조표 | 표준값 조회 시 | StandardTable |
| Information | INF | 프로세스 메타정보 | 프로젝트 정보 관리 | Info |
| Mapping | MAP | 매핑 정보 | 데이터 매핑 시 | 문자열(string) |

---

## 내부 구조 개요

```
wai/
├── __init__.py                # 주요 객체 및 함수 export
├── gv.py                      # 글로벌 변수 저장용 싱글톤
├── iid.py                     # 인스턴스 ID 관리
├── singleton_dot_dict.py      # 싱글톤 dict 구조
├── unit.py                    # 단위 Enum 정의
├── value_objects.py           # 값 타입 정의 (SingleValue, RangedValue 등)
├── wai_containers.py          # DCN, DCP, DCR, STC, EQP, DSP, DEP, STD, INF 컨테이너 정의
├── standard.py                # 표준 참조표 관리 클래스
└── info.py                    # 프로세스 코드, 단위계, 공식 버전 관리
```

## 주요 컨테이너



### 공정계산식용 컨테이너

#### DCN (Design Conditions)
설계 조건을 관리하는 컨테이너입니다. 프로젝트의 기본 입출력 조건을 정의합니다.

**주요 속성**:
- `influents`: 유입 파라미터 (유량, 수질 등) - `SingleValue`
- `effluents`: 유출 파라미터 (방류수 수질 등) - `IValueObject`
- `efficiency`: 처리 효율 범위값 - `RangedValue`
- `returns`: 수리계산식 역전파 참조 매개변수 - `IValueObject`

**사용 예시**:
```python
from WAI import DCN, SingleValue, RangedValue

# 유입수 조건
DCN.influents.q = SingleValue("유입유량", 1200, unit="m3/d")
DCN.influents.BOD = SingleValue("유입 BOD", 200, unit="mg/L")

# 처리 효율
DCN.efficiency.BOD = RangedValue("BOD 처리효율", 95, Min=90, Max=98, unit="%")

# 유출수 조건 (첫 실행 시 생성)
DCN.effluents.water.q = DCN.influents.q
DCN.effluents.water.bod = DCN.influents.BOD

# 재계산 시 동적 값 반영
DCN.effluents.water.q = DCN.influents.q.value
DCN.effluents.water.bod = DCN.influents.BOD.value
```

#### DCR (Design Criteria)
설계 기준값을 저장합니다. 설계 시 참조하는 기준값들을 정의합니다.

**적용 가능 클래스**: `SingleValue`, `RangedValue`

**사용 예시**:
```python
from WAI import DCR, SingleValue

DCR.HRT = SingleValue("수리학적 체류시간", 8, unit="h")
DCR.SRT = SingleValue("슬러지 체류시간", 20, unit="d")
```

#### DCP (Design Parameters)
공정별 설계 매개변수를 관리합니다. 도메인별로 그룹화하여 저장합니다.

**적용 가능 클래스**: `SingleValue`, `RangedValue`, `TextValue`, `BoolValue`, `DropboxValue`

**사용 예시**:
```python
from WAI import DCP, RangedValue

# 슬러지 관련 매개변수
DCP.Sludge.MLSS = RangedValue("MLSS", 3500, Min=3000, Max=4000, unit="mg/L")

# 약품 관련 매개변수
DCP.Chemicals.PAC = SingleValue("PAC 주입률", 15, unit="mg/L")
```

#### DSP (Design Specification Parameters)
구조물의 규격 계산에 필요한 매개변수를 저장합니다. 구조물별 계산식 입력값으로 사용됩니다.

**적용 가능 클래스**: `SingleValue`, `RangedValue`, `TextValue`, `BoolValue`, `DropboxValue`

**사용 예시**:
```python
from WAI import DSP, DCN, SingleValue

# SBR 탱크 규격 매개변수 선언 (첫 실행 시 생성)
DSP.SBR_Tank.Flowrate = SingleValue("Flowrate", 0, False, unit="m³/d", remark="유량")
DSP.SBR_Tank.Volume = SingleValue("Volume", 0, False, unit="m³", remark="용량")

# 재계산 시 동적 값 반영 (float, int 등 기본 타입 사용)
DSP.SBR_Tank.Flowrate = DCN.influents.q.value
DSP.SBR_Tank.Volume = DSP.SBR_Tank.Flowrate.value * 6 / 24  # HRT 6시간 적용
```

#### DEP (Design Equipment Parameters)
기계설비의 설계 매개변수를 관리합니다. 설비별 성능, 규격, 운영 조건을 저장합니다.

**적용 가능 클래스**: `SingleValue`, `RangedValue`, `TextValue`, `BoolValue`, `DropboxValue`

**사용 예시**:
```python
from WAI import DEP, DSP, SingleValue

# 펌프 설계 매개변수 선언 (첫 실행 시 생성)
DEP.MainPump.Inflow_Flowrate = SingleValue("Pump_Flowrate", 0, False, unit="m³/d", remark="유입량")
DEP.MainPump.Safety_Factor = SingleValue("Safety_Factor", 20, True, unit="%", remark="여유율")

# 재계산 시 동적 값 반영 (float, int 등 기본 타입 사용)
DEP.MainPump.Inflow_Flowrate = DSP.SBR_Tank.Flowrate.value
```

### 구조물 및 설비용 컨테이너

#### STC (Structure) - StructureValue

구조물 정보를 `StructureValue` 객체로 관리합니다.

**적용 가능 클래스**: `StructureValue`

> 💡 **계산식 자동 전달**: Structure 계산식 실행 시 `inputs`에 구조물 속성이 자동 통합되어 전달됩니다.

> 💡 **규격 자동 계산**: W, L, Diameter은 프로그램에서 입력을 받기 전까지 자동으로 계산됩니다. 사용자가 특정 사이즈를 입력하면 고정됩니다.

**구조물 타입**: `CONCRETE_SQUARE`, `SUS_TANK_SQUARE`, `SUS_TANK_CIRCULAR`, `SKID`

**주요 속성**:

| 속성 | 타입 | 설명 |
|------|------|------|
| `name` | str | 구조물명 |
| `code_key` | StructureType | 구조물 타입 |
| `tank_number_list` | list[int] | 선택 가능한 지수 목록 |
| `water_level` | SingleValue | 수위 (m) |
| `height` | SingleValue | 높이 (m) |
| `W`, `L` | SingleValue | 폭, 길이 (m) |
| `required_capacity` | SingleValue | 설계 요구 용량 (m³) |
| `applied_capacity` | SingleValue | 실제 적용 용량 (m³) |
| `inputs` | SingletonDotDict | DSP 컨테이너 입력값 |
| `forward_result` | SingletonDotDict | 규격계산식 결과 |
| `level_result` | SingletonDotDict | 수리계산식 파라미터 결과 |
| `level_drawing` | SingletonDotDict | 수리계산식 드로잉 결과 |

**사용 예시**:
```python
from WAI import STC, DSP, DCN, StructureValue, StructureType, SingleValue

# DSP 매개변수 설정
DSP.tank.volume = SingleValue("Volume", 0, False, unit="m³")
DSP.tank.volume = DCN.influents.q.value * 6 / 24  # 재계산 시 동적 값 반영 (HRT 6시간)

# 구조물 정의
STC.tank = StructureValue(
    name="유량조정조",
    code_key_list=[StructureType.CONCRETE_SQUARE, StructureType.SKID],
    code_key=StructureType.CONCRETE_SQUARE,
    tank_number_list=[1, 2, 4],
    water_level=5.0,
    height=6.0,
    width=8.0,
    length=7.0,
    # diameter= 3.0,
    required_capacity=DSP.tank.volume.value,
    inputs=DSP.tank
)
# 재계산 시 동적 값 반영 (필수!)
STC.tank.required_capacity = DSP.tank.volume.value

# 값 접근
print(STC.tank.W.value)  # 8.0
print(STC.tank.applied_capacity.value)  # 계산된 적용 용량

# 계산 결과 접근
elevation = SingleValue("elevation", 5.0, False, unit="m")
elevation.value = STC.tank.level_result.get("elevation", elevation.value)
```

> 📖 **상세 속성 및 자동 전달**: [StructureValue - 구조물 통합 관리](#structurevalue---구조물-통합-관리) 참조

#### EQP (Equipment) - EquipmentValue

기계설비 정보를 `EquipmentValue` 객체로 관리합니다.

**적용 가능 클래스**: `EquipmentValue`

> 💡 **계산식 자동 전달**: Equipment 계산식 실행 시 `inputs`에 설비 속성이 자동 통합되어 전달됩니다.

**주요 속성**:

| 속성 | 타입 | 설명 |
|------|------|------|
| `name` | str | 설비명 |
| `code_key` | str | 설비 코드 |
| `normal_count` | SingleValue | 상용 대수 |
| `spare_count` | SingleValue | 예비 대수 |
| `total_required_capacity` | SingleValue | 전체 필요용량 |
| `operation_time` | SingleValue | 가동시간 (기본값: 10.0 hr) |
| `inputs` | SingletonDotDict | DEP 컨테이너 입력값 |
| `outputs` | SingletonDotDict | 계산 결과 |
| `structure` | StructureValue | 연관 구조물 (선택) |

**사용 예시**:
```python
from WAI import EQP, DEP, STC, DSP, EquipmentValue, SingleValue

# DEP 매개변수 설정
DEP.pump.flowrate = SingleValue("Flowrate", 0, False, unit="m³/d")
DEP.pump.flowrate = DSP.eqtank.Flowrate_Eqtank.value  # 재계산 시 동적 값 반영

# 기계설비 정의
EQP.pump = EquipmentValue(
    name="유출펌프",
    code_key_list=["M_PMP0601", "M_PMP0302"],
    code_key="M_PMP0601",
    normal_count=2,
    spare_count=1,
    total_required_capacity=DEP.pump.flowrate.value,
    unit="대",
    operation_time=10.0,  # 가동시간 (hr)
    inputs=DEP.pump,
    structure=STC.tank  # 연관 구조물 (선택)
)
# 재계산 시 동적 값 반영 (필수!)
EQP.pump.total_required_capacity = DEP.pump.flowrate.value

# 계산 결과 접근
power = SingleValue("power",10,False, unit="W")
power.value = EQP.pump.outputs.get("power", power.value)
```

> 📖 **상세 속성 및 자동 전달**: [EquipmentValue - 기계설비 통합 관리](#equipmentvalue---기계설비-통합-관리) 참조

### 표준 참조표 및 정보 컨테이너

#### STD (Standard)
표준 참조표를 관리합니다. `StandardTable` 클래스를 통해 표준값을 조회할 수 있습니다.

**적용 가능 클래스**: `StandardTable`

> ⚠️ **글로벌 컨테이너**: STD는 인스턴스 스코프가 아닌 **전역 컨테이너**입니다. 동일한 이름으로 한 번만 등록 가능하며, 다른 규격표를 사용할 경우 다른 이름으로 등록해야 합니다.

**사용 예시**:
```python
from WAI import STD, StandardTable

# 단순 테이블 (구간값만 사용)
simple_table_data = {
    "name": "pipe_friction",
    "table": {
        0.0: 100,
        1.0: 150,
        2.0: 200
    }
}
STD.pipe_friction = StandardTable(simple_table_data)  # 전역 등록 (한 번만 가능)
friction_value = STD.pipe_friction.get_value(1.5)  # 구간값 1.5에 해당하는 값 조회

# 지수 테이블 (구조물 지수 + 구간값 사용)
index_table_data = {
    "name": "capacity_table",
    "table": {
        1: {0.0: 100, 1.0: 200},  # 구조물 지수 1
        2: {0.0: 300, 1.0: 400}   # 구조물 지수 2
    }
}
STD.capacity_table = StandardTable(index_table_data)  # 전역 등록 (한 번만 가능)
capacity = STD.capacity_table.get_value(2, 0.5)  # 구조물 지수 2, 구간값 0.5

# 해당 공정에서만 사용할 경우 (로컬 변수로 사용)
local_table = StandardTable(index_table_data)  # STD 없이 로컬 변수로 사용
local_capacity = local_table.get_value(2, 0.5)
```

#### INF (Information)
프로세스의 메타 정보를 관리합니다. 프로젝트 코드, 단위계, 버전, 작성자 등을 저장합니다.

**적용 가능 클래스**: `Info`

**사용 예시**:
```python
from WAI import INF, Info, UnitSystemType

INF.Info = Info(
    process_code="Equalization tank",
    unit_system=UnitSystemType.METRIC,
    formula_version="v1.2.0",
    author="홍길동",
    date="2024-12-19"
)
```

#### MAP (Mapping)
데이터 매핑 및 연결 정보를 관리합니다. 주로 문자열(string) 정보를 저장하는 용도로 사용됩니다.

**적용 가능 타입**: `str` (문자열)

**사용 예시**:
```python
from WAI import MAP

# 매핑 정보 저장
MAP.tank_A = "유량조정조"
MAP.pump_B = "유출펌프"
```

#### HWL (Height Width Length)

3D 모델링에 필요한 치수 정보(height, width, length 등)를 전달하기 위한 컨테이너입니다.

**적용 가능 클래스**: `SingleValue`

**특징**:
- 3D 모델링 시스템과의 데이터 전달 용도

**사용 예시**:
```python
from WAI import HWL, SingleValue

# 3D 모델링 치수 정보 설정 (HWL.속성 형태)
HWL.Waterlevel = SingleValue("수위", DSP.eqtank.level_result.value, False)
HWL.Waterlevel.value = DSP.eqtank.level_result.value
```

#### OPX (Operation Expense)

> 💡 **신규 추가**: v0.1.17

유지비용 계산에 필요한 매개변수를 저장하는 컨테이너입니다.

**적용 가능 클래스**: `SingleValue`

**특징**:
- 운영비용, 전력비, 약품비 등 유지관리 비용 계산 용도
- `name`, `value`, `unit`, `remark` 값이 JSON 데이터로 추출되어 유지비 내역 산출에 이용됨

**사용 예시**:
```python
from WAI import OPX, SingleValue

# 유지비용 매개변수 설정 (OPX.속성 형태)
# name 영역에 code_key로 설정
OPX.sludge = SingleValue(name="SLUDGE_U", value=1, unit="원/kg", remark="슬러지")
OPX.sludge.value = DSP.ABC.sludge_q.value

# JSON 추출 시 다음과 같이 변환됨:
# { "name": "SLUDGE_U", "value": 계산값, "unit": "원/kg", "remark": "슬러지" }
```

---

## 주요 클래스 및 구조

### 값 표현 클래스 (Value Objects)

WAI는 다양한 타입의 값을 표현하기 위한 클래스를 제공합니다.

#### 기본 값 클래스

| 클래스 | 용도 | 주요 속성 | 예시 |
|--------|------|----------|------|
| `SingleValue` | 단일 숫자 값 | value, unit | 유량: 1200 m³/d |
| `RangedValue` | 범위를 가진 값 | value, Min, Max, unit | MLSS: 3500 (3000~4000) mg/L |
| `TextValue` | 텍스트 값 | value | 제조사명: "ABC Corp" |
| `BoolValue` | 불리언 값 | value | 가동여부: True |
| `DropboxValue` | 선택 목록 값 | value (리스트) | 탱크 개수: [1, 2, 4, 8] |

#### 공간/형상 클래스

| 클래스 | 용도 | 주요 속성 | 차원 |
|--------|------|----------|------|
| `Vector3Value` | 3D 좌표 | x, y, z | 3D |
| `Box3Value` | 3D 박스 영역 | min, max (Vector3) | 3D |
| `Vector2Value` | 2D 좌표 | x, y | 2D |
| `Box2Value` | 2D 박스 영역 | min, max (Vector2) | 2D |
| `ELBoxValue` | elevation level 포함 2D 박스 | min, max (Vector2), elevation_level | 2D |

#### 특수 목적 클래스

| 클래스 | 용도 | 주요 속성 |
|--------|------|----------|
| `PipeValue` | 파이프 정보 | size, unit, BM (재질) |
| `InfoValue` | 플로우 정보 전달 | size, bm, comp, raw |
| `StructureValue` | 구조물 통합 관리 | 치수, 용량, 타입 등 |
| `EquipmentValue` | 기계설비 통합 관리 | 대수, 용량, 사양 등 |

#### IValueObject 공통 속성

모든 값 객체는 다음 공통 속성을 가집니다:

| 속성 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| `name` | str | 값의 이름 | 필수 |
| `value` | Any | 실제 값 | 필수 |
| `editable` | bool | 편집 가능 여부 | True |
| `unit` | str | 단위 | "" |
| `remark` | str | 비고/설명 | "" |
| `bound` | bool | 바인딩 상태 | False |
| `display` | bool | UI 표시 여부 | True |
| `summary` | bool | 공정 요약 표시 여부 | True |

**사용 예시**:
```python
from WAI import SingleValue

# 모든 공통 속성을 활용한 예시
flow_rate = SingleValue(
    name="유입유량",
    value=1200,
    editable=False,        # 수정 불가
    unit="m3/d",
    remark="평균 유입량",
    display=True,          # UI에 표시
    summary=True           # 요약 리포트에 포함
)
```

### 숫자 표시 형식 (string_format)

`SingleValue`와 `RangedValue`는 C# 문자열 서식을 지원하여 숫자 표시 형식을 제어할 수 있습니다.

#### 주요 포맷 코드

| 포맷 코드 | 설명 | 입력 예시 | 출력 예시 |
|----------|------|----------|----------|
| `F2` | 소수점 2자리 고정 | 123.456 | 123.46 |
| `F6` | 소수점 6자리 고정 | 0.1234567 | 0.123457 |
| `N0` | 천 단위 콤마, 소수점 없음 | 1234567 | 1,234,567 |
| `N2` | 천 단위 콤마, 소수점 2자리 | 1234567.8989 | 1,234,567.90 |

> ⚠️ **주의**: 소수점 표시는 고정된 자리수까지 보여주며 마지막 자리에서 반올림 처리됩니다.

**사용 예시**:
```python
from WAI import SingleValue

# 소수점 2자리로 표시
device_count = SingleValue("Device_number", 2.0, True, unit="ea", remark="가동대수", string_format="F2")  # 출력: 2.00

# 천 단위 콤마 표시
capacity = SingleValue("Capacity", 1500000, unit="L", string_format="N0")  # 출력: 1,500,000
```

### 특수 값 클래스 상세

#### InfoValue - 플로우 정보 전달

FlowInfo 전달을 위한 구조체로, 파이프 크기, 재질, 설비명, 원료 타입 등을 문자열로 저장합니다.

> ⚠️ **속성명 변경**: `equip` 속성이 `comp`로 변경되었습니다. (v0.1.15)

**주요 속성**:
- `size` (str): 파이프 크기 (예: "150A")
- `bm` (str): 재질/규격 정보 (BM, Bill of Materials)
- `comp` (str): 설비명 (component, 기존 `equip`에서 변경)
- `raw` (str): 원료 타입 (`RawType` Enum: `WATER`, `SLUDGE`, `GAS`)

**사용 예시**:
```python
from WAI import InfoValue, RawType, PipeValue, DCN, EQP

# 물 배출 정보 설정
DCN.effluents.water.info = InfoValue("info")
pump_pipe = EQP.Sludge_Supply_Pump.outputs.get("Pump_dia",
    PipeValue("pump_pipe", 150, unit="A", BM="STS")
)

DCN.effluents.water.info.bm = pump_pipe.BM
DCN.effluents.water.info.size = f"{int(pump_pipe.size)}A"
DCN.effluents.water.info.comp = EQP.Sludge_Supply_Pump.name
DCN.effluents.water.info.raw = RawType.WATER

# 슬러지 배출 정보 설정
DCN.effluents.sludge.info = InfoValue("info")
DCN.effluents.sludge.info.bm = pump_pipe.BM
DCN.effluents.sludge.info.size = f"{int(pump_pipe.size)}A"
DCN.effluents.sludge.info.raw = RawType.SLUDGE
```

#### DropboxValue - 드롭다운 선택

드롭다운(선택 목록) 값을 표현합니다. 단일값 또는 다중값 리스트를 지원합니다.

**사용 예시**:
```python
from WAI import DropboxValue

# 탱크 지수 선택
tank_indices = DropboxValue(name="지수", value=[1, 2, 4, 8], editable=False, remark="탱크 개수 옵션")
```

#### PipeValue - 파이프 정보

파이프(배관) 정보를 관리합니다.

**주요 속성**:
- `value`: 파이프 직경
- `unit`: 단위 (기본값: "A")
- `BM`: 재질 (예: "STS304", "PVC", "SS400")

**사용 예시**:
```python
from WAI import PipeValue

# 주배관 정의
main_pipe = PipeValue(name="주관", value=100, unit="A", BM="STS304", editable=False)

# 직경과 재질 접근
diameter = main_pipe.value  # 100
material = main_pipe.BM     # "STS304"
```

### 공간 및 형상 클래스

#### Vector3Value - 3차원 좌표

3차원 공간의 점이나 방향을 표현합니다.

**생성 방법**:
```python
from WAI import Vector3Value

# 방법 1: 개별 좌표로 생성
position = Vector3Value(10.5, 20.0, 5.2)

# 방법 2: 튜플과 이름으로 생성
center = Vector3Value((0, 0, 0), "중심점")
```

**좌표 접근**:
```python
x = position.x      # 10.5
y = position.y      # 20.0
z = position.z      # 5.2
coords = position.value  # (10.5, 20.0, 5.2)
```

#### Box3Value - 3차원 박스

3차원 공간의 직육면체 영역을 표현합니다.

**생성 및 사용**:
```python
from WAI import Box3Value

# 박스 정의 (최소 좌표, 최대 좌표)
tank_box = Box3Value("탱크", min=(0, 0, 0), max=(10, 8, 6))

# 좌표 접근
min_point = tank_box.min  # Vector3Value(0, 0, 0)
max_point = tank_box.max  # Vector3Value(10, 8, 6)

# 치수 계산
width = tank_box.max.x - tank_box.min.x   # 10m
length = tank_box.max.y - tank_box.min.y  # 8m
height = tank_box.max.z - tank_box.min.z  # 6m

# 대각선 길이 계산
diff = tank_box.max - tank_box.min
diagonal_length = (diff.x**2 + diff.y**2 + diff.z**2)**0.5
```

#### Vector2Value / Box2Value - 2차원

2D 설계에서 사용되는 좌표와 영역을 표현합니다.

**사용 예시**:
```python
from WAI import Vector2Value, Box2Value

# 2D 좌표
point = Vector2Value(10.5, 20.0)
x = point.x
y = point.y

# 2D 영역
area = Box2Value("평면도", min=(0, 0), max=(100, 100))
```

#### ELBoxValue - elevation level 포함 2D 박스

`Box2Value`를 상속하며, elevation level 정보를 추가로 포함합니다.

**주요 속성**:
- `min`: 최소 좌표 (Vector2Value)
- `max`: 최대 좌표 (Vector2Value)
- `elevation_level`: elevation level (float, 기본값: 5.0)

**사용 예시**:
```python
from WAI import Vector2Value, ELBoxValue

# elevation level 포함 2D 영역
level_area = ELBoxValue("수위면", min=Vector2Value(0, 0), max=Vector2Value(100, 100), elevation_level=3.5)
```

### StructureValue - 구조물 통합 관리

구조물 정보를 체계적으로 관리하는 클래스입니다. 기본 사용법은 [STC (Structure)](#stc-structure---structurevalue) 참조.

> 💡 **계산식 자동 전달**: StructureValue는 Structure 계산식 파일 실행 시 자동으로 치수/용량 정보를 `inputs` 매개변수에 통합하여 전달합니다.

#### 주요 속성 구조

##### 1. 메타 정보

| 속성 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `name` | str | 구조물명 | "반응조" |
| `code_key_list` | list | 선택 가능한 타입 목록 | [CONCRETE_SQUARE, SKID] |
| `code_key` | StructureType | 적용된 구조물 타입 | CONCRETE_SQUARE |

**구조물 타입**: `SUS_TANK_SQUARE`, `CONCRETE_SQUARE`, `SUS_TANK_CIRCULAR`, `SKID`

> ⚠️ **SKID 타입**: 계산식 없이 `level_result`/`level_drawing`에 직접 값 설정 가능. 사용 전 `clear()` 호출 필수. [SKID 타입 사용법](#skid-타입-사용법) 참조.

##### 2. 지수 및 레이아웃 정보

| 속성 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| `tank_number_list` | list[int] | 선택 가능한 지수 | [] |
| `tank_number` | SingleValue | 적용 지수 (ea) | list[0], editable=True |
| `layout_type` | StructureLayoutType | 3D 레이아웃 타입 | None-Type |
| `layout_type_number` | int | 레이아웃 세부 지수 | - |
| `standard_table` | StandardTable | 참조 표준표 | - |

**레이아웃 타입**: `A_TYPE`, `B_TYPE`, `C_TYPE`, `D_TYPE`, `E_TYPE`, `F_TYPE`, `G_TYPE`, `H_TYPE`, `None-Type`

##### 3. 용량 및 치수 (모두 SingleValue)

| 속성 | 단위 | editable | 설명 |
|------|------|----------|------|
| `water_level` | m | True | 수위 (기본: 5.0) |
| `height` | m | True | 높이 (기본: 0.0, 미입력 시 water_level + 1.0으로 계산) |
| `required_capacity` | m³ | False | 설계 요구 용량 (기본: 500.0) |
| `applied_capacity` | m³ | False | 실제 적용 용량 (계산으로 결정) |
| `W` | m | True | 폭 (기본: 0.0, 미입력 시 계산으로 결정) |
| `L` | m | True | 길이 (기본: 0.0, 미입력 시 계산으로 결정) |
| `diameter` | m | True | 직경 (기본: 0.0, 미입력 시 계산으로 결정) |

##### 4. 계산식 정보

| 속성 | 타입 | 설명 |
|------|------|------|
| `inputs` | SingletonDotDict | DSP 컨테이너 입력값 (사용자 정의) |
| `forward_result` | SingletonDotDict | 규격계산식 결과 (Box3Value) |
| `reverse_result` | BoolValue | 검증계산식 결과 (Pass/Fail) |
| `level_result` | SingletonDotDict | 수리계산식 파라미터 결과 (SingleValue 등) |
| `level_drawing` | SingletonDotDict | 수리계산식 드로잉 결과 (Box2Value, ELBoxValue) |

##### 5. 계산식에 자동 전달되는 속성

Structure 계산식 실행 시, StructureValue는 다음 속성들을 자동으로 `DSP` 매개변수에 포함하여 전달합니다:

| 속성명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `W` | SingleValue | 구조물 폭 | m |
| `L` | SingleValue | 구조물 길이 | m |
| `diameter` | SingleValue | 구조물 직경 (원형) | m |
| `water_level` | SingleValue | 수위 | m |
| `height` | SingleValue | 높이 | m |
| `tank_number` | SingleValue | 구조물 지수 (개수) | ea |
| `required_capacity` | SingleValue | 설계 요구 용량 | m³ |
| `applied_capacity` | SingleValue | 실제 적용 용량 | m³ |
| `layout_type_number` | SingleValue | 레이아웃 타입 번호 | ea |
| `pipe_length` | SingleValue | 배관 길이 | m |
| `pipe_size` | SingleValue | 관경 | A |
| `tee_joint_count` | SingleValue | T자 피팅 개수 | ea |
| `elbow_count` | SingleValue | Elbow 개수 | ea |
| `pipe_max_height` | SingleValue | 배관 최대 높이 | m |
| `pipe_min_height` | SingleValue | 배관 최소 높이 | m |
| `elevation_level` | SingleValue | elevation level | m |
| `head_loss` | SingleValue | 수두 손실 | m |

> 💡 **Pipe 정보**: `pipe_length`, `pipe_size`, `tee_joint_count`, `elbow_count`, `pipe_max_height`, `pipe_min_height`는 Unity에서 3D 모델링 이후 자동으로 생성되는 값들입니다. 이 값들은 Structure 계산식에 자동으로 전달되어 활용할 수 있습니다.

> 💡 **수리양정 정보**: `elevation_level`과 `head_loss`는 수리양정 계산에 사용되는 값입니다. `elevation_level` 초기값은 5.0, `head_loss` 초기값은 0.0 입니다. Structure 계산식에 자동으로 전달되어 활용할 수 있습니다.


#### 공정 계산식에서의 사용 예시

```python
from WAI import STC, DSP, DCN, StructureValue, StructureType, SingleValue

# DSP에 매개변수 설정
DSP.reaction_tank.Flowrate_Eqtank = SingleValue("Flowrate_Eqtank", 0, False, unit="m³/d", remark = "유량", summary=False, display=False)
DSP.reaction_tank.Flowrate_Eqtank_hr = SingleValue("Flowrate_Eqtank_hr", 0, False, unit="m³/h", remark = "유량", summary=False, display=False)
DSP.reaction_tank.Final_Req_Vol = SingleValue("Final_Req_Vol", 0, False, unit="m³", remark = "설계 용량")

# 재계산 시 동적 값 반영 (float, int 등 기본 타입 사용)
DSP.reaction_tank.Flowrate_Eqtank = DCN.influents.q.value
DSP.reaction_tank.Flowrate_Eqtank_hr = DSP.reaction_tank.Flowrate_Eqtank.value / 24
DSP.reaction_tank.Final_Req_Vol = DSP.reaction_tank.Flowrate_Eqtank_hr.value * 6  # HRT 6시간

# 구조물 정의
STC.reaction_tank = StructureValue(
    name="반응조",
    code_key_list=[StructureType.CONCRETE_SQUARE, StructureType.SKID],
    code_key=StructureType.CONCRETE_SQUARE,
    tank_number_list=[1, 2, 4],  # 첫 번째 값(1)이 기본값
    water_level=6.0,
    width=8.0,
    length=7.0,
    height=7.0,
    required_capacity=DSP.reaction_tank.Final_Req_Vol.value,
    inputs=DSP.reaction_tank  # DSP 컨테이너 전달
)
# 재계산 시 동적 값 반영 (float, int 등 기본 타입 사용)
STC.reaction_tank.required_capacity = DSP.reaction_tank.Final_Req_Vol.value

# 값 접근
tank_width = STC.reaction_tank.W.value  # 8.0
tank_height = STC.reaction_tank.height.value  # 7.0
```

#### SKID 타입 사용법

SKID 타입의 StructureValue는 `level_calculate` 계산식 없이 `level_result`와 `level_drawing`에 직접 접근하여 값을 설정할 수 있습니다.

##### 특징

| 항목 | 일반 구조물 타입 | SKID 타입 |
|------|-----------------|-----------|
| `level_result` / `level_drawing` | 계산식 실행 후 생성 | 접근 시 자동 생성 |
| `level_calculate` 실행 | 필수 | 불필요 |
| 직접 값 설정 | 불가 | 가능 |

##### 사용 예시

```python
from WAI import STC, StructureValue, StructureType, SingleValue, Vector2Value, Box2Value, ELBoxValue

# SKID 타입 구조물 생성
STC.screen_skid = StructureValue(
    name="협잡물처리기 SKID",
    code_key_list=[StructureType.SKID],
    code_key=StructureType.SKID,
    tank_number_list=[1],
    water_level=2.0,
    required_capacity=50.0
)

# SKID 타입인 경우 level_result/level_drawing 직접 설정
if STC.screen_skid.code_key == StructureType.SKID.value:
    # 재계산 시 기존 값 초기화
    STC.screen_skid.level_result.clear()
    STC.screen_skid.level_drawing.clear()

    # level_result에 값 설정
    STC.screen_skid.level_result.inlet_level = SingleValue("inlet_level", 1.5, unit="m")
    STC.screen_skid.level_result.outlet_level = SingleValue("outlet_level", 4.8, unit="m")

    # level_drawing에 Box2Value 설정
    STC.screen_skid.level_drawing.Level1 = Box2Value(
        "Level1", Vector2Value(0, 0), Vector2Value(100, 100)
    )
    STC.screen_skid.level_drawing.Level2 = ELBoxValue(
        "Level2", Vector2Value(10, 10), Vector2Value(90, 90), elevation_level=3.5
    )

# 계산 결과 접근
print(STC.screen_skid.level_result.inlet_level.value)  # calculated_inlet_level 값                                                                                                                    
print(STC.screen_skid.level_result.outlet_level.value)  # calculated_outlet_level 값                                                                                                                    
print(STC.screen_skid.level_drawing.Level2.elevation_level)  # 3.5
```

### EquipmentValue - 기계설비 통합 관리

기계설비 정보를 체계적으로 관리하는 클래스입니다. 기본 사용법은 [EQP (Equipment)](#eqp-equipment---equipmentvalue) 참조.

> 💡 **계산식 자동 전달**: EquipmentValue는 Equipment 계산식 파일 실행 시 자동으로 설비 사양 정보를 `inputs` 매개변수에 통합하여 전달합니다.

#### 주요 속성 구조

##### 1. 메타 정보

| 속성 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `name` | str | 설비명 | "주펌프" |
| `code_key_list` | list[str] | 선택 가능한 코드 목록 | ["M_PMP01", "M_PMP02"] |
| `code_key` | str | 적용된 설비 코드 | "M_PMP01" |
| `unit_required_capacity` | str | 대당 소요용량 (UI 표시용) | f"{DSP.Pump.result_A.value}m3/min" |
| `structure` | StructureValue | 포함된 구조물 (선택사항) | STC.tank |

##### 2. 사양 정보 (모두 SingleValue/TextValue)

| 속성 | 단위 | 설명 |
|------|------|------|
| `normal_count` | ea | 상용 대수 |
| `spare_count` | ea | 예비 대수 |
| `total_required_capacity` | m³/hr | 전체 필요용량 |
| `operation_time` | hr | 가동시간 |
| `manufacturer` | - | 적용 업체 (TextValue) |
| `model_name` | - | 적용 모델 (TextValue) |
| `unit_price` | 원 | 단가 |

> 💡 **신규 추가**: `operation_time` 속성이 추가되었습니다. (v0.1.17)

##### 3. 계산식 정보

| 속성 | 타입 | 설명 |
|------|------|------|
| `inputs` | SingletonDotDict | DEP 컨테이너 입력값 (사용자 정의) |
| `outputs` | SingletonDotDict | 계산 결과 (딕셔너리 형태) |

##### 4. 계산식에 자동 전달되는 속성

Equipment 계산식 실행 시, EquipmentValue는 다음 속성들을 자동으로 `DEP` 매개변수에 포함하여 전달합니다:

| 속성명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `normal_count` | SingleValue | 상용 대수 | ea |
| `spare_count` | SingleValue | 예비 대수 | ea |
| `total_required_capacity` | SingleValue | 전체 필요용량 | m³/hr |
| `operation_time` | SingleValue | 가동시간 | hr |
| `manufacturer` | TextValue | 적용 업체 | - |
| `model_name` | TextValue | 적용 모델 | - |
| `unit_price` | SingleValue | 단가 | 원 |
| `power_kW` | SingleValue | 전력 | kW |
| `tag_number` | SingleValue | 태그 번호 | ea |
| `spec1` | TextValue | 규격 | - |
| `spec2` | TextValue | 사양 | - |
| `qty` | SingleValue | 수량 (상용+예비) | ea |
| `pipe_length` | SingleValue | 배관 길이 | m |
| `pipe_size` | SingleValue | 관경 | A |
| `tee_joint_count` | SingleValue | T자 피팅 개수 | ea |
| `elbow_count` | SingleValue | Elbow 개수 | ea |
| `pipe_max_height` | SingleValue | 배관 최대 높이 | m |
| `pipe_min_height` | SingleValue | 배관 최소 높이 | m |
| `elevation_level` | SingleValue | elevation level | m |
| `head_loss` | SingleValue | 수두 손실 | m |

> 💡 **Pipe 정보**: `pipe_length`, `pipe_size`, `tee_joint_count`, `elbow_count`, `pipe_max_height`, `pipe_min_height`는 Unity에서 3D 모델링 이후 자동으로 생성되는 값들입니다. 이 값들은 Equipment 계산식에 자동으로 전달되어 계산에 활용할 수 있습니다.

> 💡 **수리양정 정보**: `elevation_level`과 `head_loss`는 수리양정 계산에 사용되는 값입니다. `elevation_level` 초기값은 5.0, `head_loss` 초기값은 0.0 입니다. Equipment 계산식에 자동으로 전달되어 활용할 수 있습니다.

#### 공정 계산식에서의 사용 예시

```python
from WAI import EQP, DEP, STC, EquipmentValue, SingleValue

# DEP에 매개변수 설정
DEP.main_pump.flowrate = SingleValue("유량", 100, unit="m³/hr")
DEP.main_pump.head = SingleValue("양정", 15, unit="m")
DEP.main_pump.efficiency = SingleValue("효율", 75, unit="%")

# 기계설비 정의 (구조물 포함)
EQP.main_pump = EquipmentValue(
    name="주펌프",
    code_key_list=["M_PMP080301", "M_PMP080302"],
    code_key="M_PMP080301",
    normal_count=2,
    spare_count=1,
    total_required_capacity=DEP.main_pump.flowrate.value,
    operation_time=8.0,  # 가동시간 (기본값: 10.0 hr)
    inputs=DEP.main_pump,
    structure=STC.pump_station  # 구조물 연계
)
# 재계산 시 동적 값 반영
EQP.main_pump.total_required_capacity = DEP.main_pump.flowrate.value

# 구조물 없는 경우
EQP.blower = EquipmentValue(
    name="송풍기",
    code_key_list=["M_BLW01", "M_BLW02"],
    code_key="M_BLW01",
    normal_count=2,
    spare_count=1,
    total_required_capacity=DEP.blower.air_flowrate.value,
    inputs=DEP.blower
    # structure 생략
)
# 재계산 시 동적 값 반영
EQP.blower.total_required_capacity = DEP.blower.air_flowrate.value

# 계산 결과 접근
power = SingleValue("power",10,False, unit="W")
power.value = EQP.pump.outputs.get("power", power.value)
```

### 유틸리티 클래스

#### GV (Global Variables)
전역 데이터를 저장하는 싱글톤 컨테이너입니다.

```python
from WAI import GV, SingleValue

# 전역 변수 저장
GV["safety_factor"] = 1.2
GV.design_temperature = SingleValue("설계온도", 20, unit="°C")

# 접근
factor = GV["safety_factor"]
temp = GV.design_temperature.value
```

#### Info
프로세스의 메타 정보를 관리합니다.

```python
from WAI import Info, UnitSystemType

info = Info(
    process_code="WWTP_2024_001",
    unit_system=UnitSystemType.METRIC,  # 또는 USCS
    formula_version="v1.2.0",
    author="홍길동",
    date="2024-12-19"
)
```

#### StandardTable
표준 참조표를 관리하고 조회하는 클래스입니다. JSON 또는 딕셔너리 형태로 테이블을 생성할 수 있습니다.

**주요 메서드**:
- `get_value(*args)`: 구간값 또는 (구조물 지수, 구간값)으로 조회
- `get_min_value(*args)`: 크거나 같은 값 찾기 (최소값 조회용)
- `describe()`: 테이블 정보 출력

```python
from WAI import STD, StandardTable

# 단순 테이블 생성 (구간값만 사용)
simple_data = {
    "name": "friction_coefficient",
    "table": {
        0.0: 100,
        1.0: 150,
        2.0: 200,
        3.0: 250
    }
}
STD.friction = StandardTable(simple_data)
value = STD.friction.get_value(1.5)  # 구간값 조회: 150 반환
min_value = STD.friction.get_min_value(1.5)  # 크거나 같은 값: 150 반환

# 지수 테이블 생성 (구조물 지수 + 구간값)
index_data = {
    "name": "tank_capacity",
    "table": {
        1: {0.0: 100, 1.0: 200, 2.0: 300},  # 지수 1
        2: {0.0: 300, 1.0: 400, 2.0: 500},  # 지수 2
        4: {0.0: 600, 1.0: 800, 2.0: 1000}  # 지수 4
    }
}
STD.tank_capacity = StandardTable(index_data)
capacity = STD.tank_capacity.get_value(2, 1.5)  # 지수 2, 구간값 1.5: 400 반환
```

#### 기타

- `Unit`: 단위 표기를 위한 Enum
- `SingletonDotDict`: 타입 검사를 포함한 딕셔너리 구조
- `UnitSystemType`: 단위계 타입 (`METRIC`, `USCS`)

---

## 계산식 작성 가이드

WAI 모듈에서는 세 가지 종류의 계산식 파일(.py)을 작성할 수 있습니다:

1. **Process (공정 계산식)**: 공정 전체의 설계 조건, 매개변수, 기준을 계산
2. **Structure (구조물 계산식)**: 구조물의 3D 형상, 용량 검증, 수리 계산
3. **Equipment (기계설비 계산식)**: 기계설비의 용량, 규격, 사양 계산

### 계산식 함수 정의 규칙

각 계산식 파일에서 정의해야 하는 함수는 다음과 같습니다:

| 계산식 종류 | forward_calculate | reverse_calculate | level_calculate | 비고 |
|-----------|-------------------|-------------------|-----------------|------|
| Process | - | - | - | - |
| Structure | ✅ 필수 | ✅ 필수 | ✅ 필수 | 세 함수 모두 필수 |
| Equipment | ✅ 필수 | - | - | forward만 필수 |

**함수 설명**:
- `forward_calculate`: 입력값을 받아 구조물/설비의 규격을 계산 (규격계산식)
- `reverse_calculate`: 규격계산 결과가 요구사항을 만족하는지 검증 (검증계산식, Structure만 해당)
- `level_calculate`: 수위 및 레벨 관련 계산 (수리계산식, Structure만 해당). 결과는 `(level_result, level_drawing)` 튜플 형태로 반환

> 💡 **Process 계산식**은 특정 함수명 없이 자유롭게 작성할 수 있습니다. 공정 전체의 설계 조건, 매개변수, 기준을 정의하는 스크립트 형태로 작성합니다.


### Process 계산식 예시

```python
import WAI
from WAI import (
    DCN, DCR, DCP, DSP, DEP, STC, EQP, INF,
    SingleValue, RangedValue, StructureValue, EquipmentValue,
    StructureType, Info, UnitSystemType, Unit
)

# Step 1: 프로세스 정보 설정
# (인스턴스 ID는 Unity에서 자동 관리됨)
INF.Info = Info(
    process_code="EqualizationTank",
    unit_system=UnitSystemType.METRIC,
    formula_version="v2.0.0",
    author="홍길동",
    date="2025-10-16"
)

# Step 2: 설계 조건 입력
DCN.influents.q = SingleValue("Q", 579.5, False, "㎥/d")
DCN.influents.bod = SingleValue("BOD", 207.0, False, "mg/L")
DCN.influents.cod = SingleValue("COD", 300.0, False, "mg/L")
DCN.influents.ss = SingleValue("SS", 172.0, False, "mg/L")
DCN.influents.temp = SingleValue("Temperature", 12, False, unit=Unit.CELSIUS)

# 유출수 선언 (water 그룹화)
DCN.effluents.water.q = DCN.influents.q
DCN.effluents.water.bod = DCN.influents.bod
DCN.effluents.water.cod = DCN.influents.cod
DCN.effluents.water.ss = DCN.influents.ss

# 재계산 시 동적 값 반영 (유입수 변경 시 유출수도 갱신)
DCN.effluents.water.q = DCN.influents.q.value
DCN.effluents.water.bod = DCN.influents.bod.value
DCN.effluents.water.cod = DCN.influents.cod.value
DCN.effluents.water.ss = DCN.influents.ss.value

# 제거효율 설정
DCN.efficiency.bod = RangedValue("BOD", 0, True, 0, 0, unit="%")
DCN.efficiency.cod = RangedValue("COD", 0, True, 0, 0, unit="%")
DCN.efficiency.ss = RangedValue("SS", 0, True, 0, 0, unit="%")

# Step 3: 설계 매개변수 설정
DCP.HRT.HRT_Eqtank = RangedValue("HRT", 6, True, 3, 24, unit="h")
DCP.HRT.HRT_pHtank = RangedValue("HRT", 0.1, True, 0.1, 0.5, unit="h")

# Step 4: 구조물 규격 매개변수 계산 (DSP)
DSP.eqtank.Flowrate_Eqtank = SingleValue("Flowrate_Eqtank", 0, False, unit="m³/d", remark="유량")
DSP.eqtank.Flowrate_Eqtank_hr = SingleValue("Flowrate_Eqtank_hr", 0, False, unit="m³/h", remark="유량")
DSP.eqtank.Final_Req_Vol = SingleValue("Final_Req_Vol", 0, False, unit="m³", remark="설계 용량")

DSP.eqtank.Flowrate_Eqtank = DCN.influents.q.value
DSP.eqtank.Flowrate_Eqtank_hr = DCN.influents.q / 24  # m³/h
DSP.eqtank.Final_Req_Vol = DCP.HRT.HRT_Eqtank * DSP.eqtank.Flowrate_Eqtank_hr.value  # m³

# Step 5: 구조물 정의
STC.eqtank = StructureValue(
    name="Equalization tank",
    code_key_list=[StructureType.CONCRETE_SQUARE, StructureType.SKID],
    code_key=StructureType.CONCRETE_SQUARE,
    tank_number_list=[1, 2, 4],
    water_level=2.3,
    height=3.5,
    width=10.8,
    length=6.5,
    required_capacity=DSP.eqtank.Final_Req_Vol.value,
    inputs=DSP.eqtank
)
# 재계산 시 동적 값 반영 (생성자는 첫 생성 시에만 적용됨)
STC.eqtank.required_capacity = DSP.eqtank.Final_Req_Vol.value

# Step 6: 설계 기준 검토 (DCR)
DSP.eqtank.Actual_HRT = SingleValue("Actual_HRT", 0, False, unit="h", remark="실 체류시간")
DSP.eqtank.Actual_HRT = STC.eqtank.applied_capacity / DCN.influents.q / 24  # hr

DCR.Designed_HRT = RangedValue("Designed HRT", 0, False, 3, 24, unit="h", remark="-")
DCR.Designed_HRT = DSP.eqtank.Actual_HRT.value


# Step 7: 기계설비 매개변수 설정 (DEP)
DEP.Sludge_Discharge_Pump.Inflow_Flowrate = SingleValue("Pump_Flowrate", 0, False, unit="m³/d", remark="유입량")
DEP.Sludge_Discharge_Pump.normal_count = SingleValue("Device_number", 2, True, unit="ea", remark="가동대수")
DEP.Sludge_Discharge_Pump.Safety_Factor = SingleValue("Safety_Factor", 20.00, True, unit="%", remark="여유율")
DEP.Sludge_Discharge_Pump.Total_Dynamic_Head = SingleValue("Total Dynamic Head", 10.00, True, unit="m", remark="실양정")

DEP.Sludge_Discharge_Pump.Inflow_Flowrate = DSP.eqtank.Flowrate_Eqtank.value

# Step 8: 기계설비 정의
EQP.Sludge_Discharge_Pump = EquipmentValue(
    name="유량조정조 유출펌프",
    code_key_list=["M_PMP0601", "M_PMP0302"],
    code_key="M_PMP0601",
    normal_count=2,
    spare_count=1,
    total_required_capacity=DEP.Sludge_Discharge_Pump.Inflow_Flowrate.value,
    inputs=DEP.Sludge_Discharge_Pump,
    structure=STC.eqtank
)
# 재계산 시 동적 값 반영 (생성자는 첫 생성 시에만 적용됨)
EQP.Sludge_Discharge_Pump.total_required_capacity = DEP.Sludge_Discharge_Pump.Inflow_Flowrate.value

```

---


### 구조물 계산식 작성 예시

#### 1. 규격계산식 (forward_calculate)

입력값을 받아 구조물의 3D 형상을 계산합니다.

```python
from WAI import SingleValue, GV, Vector3Value, Box3Value, SingletonDotDict

def forward_calculate(
    DSP: SingletonDotDict = SingletonDotDict(),
    result: SingletonDotDict = SingletonDotDict(Box3Value)
):

    """
    구조물의 3D 형상(벽체, 바닥, 천장)을 계산합니다.

    Parameters:
        DSP: StructureValue의 inputs (구조물 기본 치수 및 매개변수)
        result: 계산 결과를 저장할 컨테이너

    Returns:
        result: 각 벽체의 Box3Value 형상 정보
    """

    # DSP에는 StructureValue에서 자동으로 W, L, height 등이 'm' 단위로 전달됨
    DSP.W = SingleValue("W", 8, False, unit="m")
    DSP.L = SingleValue("L", 7, False, unit="m")
    DSP.H = SingleValue("height", 6, False, unit="m")

    # 글로벌 설정값 (벽체 두께, mm 단위)
    IW = GV.IW = SingleValue("innerWidth", 300)   # 내벽 두께 (mm)
    PS = GV.PS = SingleValue("pSlab", 300)         # 바닥 슬라브 두께 (mm)
    AS = GV.AS = SingleValue("aSlab", 300)         # 천장 슬라브 두께 (mm)

    # mm 단위 변수 선언 후 계산값 할당 (result는 mm 단위로 받음)
    DSP.Wmm = SingleValue("Wmm", 0, False, unit="mm")
    DSP.Lmm = SingleValue("Lmm", 0, False, unit="mm")
    DSP.Hmm = SingleValue("Hmm", 0, False, unit="mm")

    # m → mm 변환 계산 (동적 값 반영)
    DSP.Wmm = DSP.W * 1000
    DSP.Lmm = DSP.L * 1000
    DSP.Hmm = DSP.H * 1000

    # 3D 형상 계산 (mm 단위)
    result.Floor = Box3Value("Floor", Vector3Value(0 - IW, 0 - IW, 0 - PS), Vector3Value(DSP.Wmm.value + IW, DSP.Lmm.value + IW, 0))
    result.Ceiling = Box3Value("Ceiling", Vector3Value(0 - IW, 0 - IW, DSP.Hmm.value), Vector3Value(DSP.Wmm.value + IW, DSP.Lmm.value + IW, DSP.Hmm.value + AS))
    result.FrontWall = Box3Value("FrontWall", Vector3Value(0 - IW, 0 - IW, 0), Vector3Value(DSP.Wmm.value + IW, 0, DSP.Hmm.value))
    result.RightWall = Box3Value("RightWall", Vector3Value(DSP.Wmm.value, 0, 0), Vector3Value(DSP.Wmm.value + IW, DSP.Lmm.value, DSP.Hmm.value))
    result.BackWall = Box3Value("BackWall", Vector3Value(0 - IW, DSP.Lmm.value, 0), Vector3Value(DSP.Wmm.value + IW, DSP.Lmm.value + IW, DSP.Hmm.value))
    result.LeftWall = Box3Value("LeftWall", Vector3Value(0 - IW, 0 - IW, 0), Vector3Value(0, DSP.Lmm.value, DSP.Hmm.value))

    return result
```

#### 2. 검증계산식 (reverse_calculate)

규격계산 결과가 설계 요구사항을 만족하는지 검증합니다.

```python
from WAI import SingleValue, GV, Vector3Value, Box3Value, BoolValue, SingletonDotDict

def reverse_calculate(
    DSP: SingletonDotDict = SingletonDotDict(),
    forward_result: SingletonDotDict = SingletonDotDict(Box3Value)
) -> BoolValue:

    """
    계산된 구조물이 요구 용량을 만족하는지 검증합니다.

    Parameters:
        DSP: StructureValue의 inputs (요구사항 포함)
        forward_result: 규격계산식 결과 (mm 단위 Box3Value들)

    Returns:
        BoolValue: 검증 결과 (True/False)
    """

    # DSP: StructureValue(구조물) 기본 정보 (m 단위로 전달됨)
    DSP.required_capacity = SingleValue("required_capacity", 336, False, unit="m³")

    # forward_result: 규격계산식 결과값 (mm 단위)
    # (실제로는 forward_calculate 함수의 결과가 자동으로 전달됨)
    forward_result.Floor = Box3Value("Floor", Vector3Value(-300, -300, -300), Vector3Value(8300, 7300, 0))
    forward_result.Ceiling = Box3Value("Ceiling", Vector3Value(-300, -300, 6000), Vector3Value(8300, 7300, 6300))

    # 글로벌 변수 (mm 단위)
    IW = GV.IW = SingleValue("innerWidth", 300)   # 내벽 두께 (mm)
    PS = GV.PS = SingleValue("pSlab", 300)         # 바닥 두께 (mm)

    # forward_result에서 내부 치수 계산 (mm 단위)
    inner_min_x = forward_result.Floor.min.x + IW
    inner_min_y = forward_result.Floor.min.y + IW
    inner_min_z = forward_result.Floor.min.z + PS

    inner_max_x = forward_result.Floor.max.x - IW
    inner_max_y = forward_result.Floor.max.y - IW
    inner_max_z = forward_result.Ceiling.min.z

    # 내부 용량 계산 (mm → m³ 변환)
    width_mm = abs(inner_max_x - inner_min_x)
    length_mm = abs(inner_max_y - inner_min_y)
    height_mm = abs(inner_max_z - inner_min_z)

    volume_m3 = (width_mm / 1000) * (length_mm / 1000) * (height_mm / 1000)

    # 검증: 계산 용량 >= 요구 용량
    is_sufficient = volume_m3 >= DSP.required_capacity.value

    return BoolValue("용량검증결과", is_sufficient, remark=f"계산용량: {volume_m3:.2f}m³, 요구용량: {DSP.required_capacity.value}m³")
```

#### 3. 수리계산식 (level_calculate)

수위 및 레벨 정보를 계산합니다. 결과는 `(result, drawing)` 튜플 형태로 반환합니다.

- `result`: 수리계산 파라미터 결과
- `drawing`: 2D 드로잉 정보

```python
from WAI import SingleValue, Vector2Value, Vector3Value, Box2Value, Box3Value, ELBoxValue, SingletonDotDict

def level_calculate(
    DSP: SingletonDotDict = SingletonDotDict(),
    forward_result: SingletonDotDict = SingletonDotDict(Box3Value),
    result: SingletonDotDict = SingletonDotDict(),
    drawing: SingletonDotDict = SingletonDotDict(Box2Value)
):
    """
    수위별 레벨 정보를 계산합니다.

    Parameters:
        DSP: StructureValue의 inputs
        forward_result: 규격계산식 결과 (mm 단위)
        result: 수리계산 파라미터 결과를 저장할 컨테이너
        drawing: 2D 드로잉 정보를 저장할 컨테이너 (mm 단위)

    Returns:
        (result, drawing): 튜플 형태로 반환
    """

    # DSP: StructureValue(구조물) 기본 정보 (m 단위로 전달됨)
    DSP.W = SingleValue("W", 8, False, unit="m")
    DSP.L = SingleValue("L", 7, False, unit="m")
    DSP.water_level = SingleValue("water_level", 5, False, unit="m")

    # mm 단위 변수 선언 후 계산값 할당
    DSP.Wmm = SingleValue("Wmm", 0, False, unit="mm")
    DSP.Lmm = SingleValue("Lmm", 0, False, unit="mm")
    DSP.water_level_mm = SingleValue("water_level_mm", 0, False, unit="mm")

    # m → mm 변환 계산 (동적 값 반영)
    DSP.Wmm = DSP.W * 1000
    DSP.Lmm = DSP.L * 1000
    DSP.water_level_mm = DSP.water_level * 1000

    # forward_result: 규격계산식 결과값 (mm 단위)
    forward_result.Floor = Box3Value("Floor", Vector3Value(-300, -300, -300), Vector3Value(8300, 7300, 0))
    forward_result.Ceiling = Box3Value("Ceiling", Vector3Value(-300, -300, 6000), Vector3Value(8300, 7300, 6300))

    # forward_result에서 치수 추출 (mm 단위)
    floor_min_x = forward_result.Floor.min.x
    floor_min_y = forward_result.Floor.min.y
    floor_max_x = forward_result.Floor.max.x
    floor_max_y = forward_result.Floor.max.y

    # level_result: 수리계산 파라미터 결과값 (IValueObject)
    result.elevation = SingleValue("elevation", 5.0, False, unit="m")
    result.head_loss = SingleValue("head_loss", 0.5, False, unit="m")

    # level_drawing: 2D 드로잉 결과값 (mm 단위)
    drawing.Level1 = Box2Value("Level1", Vector2Value(floor_min_x, floor_min_y), Vector2Value(floor_max_x, floor_max_y))
    drawing.Level2 = ELBoxValue("Level2", Vector2Value(0, 0), Vector2Value(DSP.Wmm.value, DSP.Lmm.value), elevation_level=3.0)

    return (result, drawing)
```

### 기계설비 계산식 작성 예시

기계설비는 규격계산식(forward_calculate)만 작성하며, 결과를 `outputs`에 저장합니다.

```python
from WAI import SingleValue, DropboxValue, SingletonDotDict
import numpy as np
import math

def forward_calculate(
    DEP: SingletonDotDict = SingletonDotDict(),
    result: SingletonDotDict = SingletonDotDict()
):
    """
    펌프의 용량과 양정을 계산합니다.
    """

    # === 1. DEP 입력값 선언 (EquipmentValue에서 자동 전달됨) ===
    DEP.Inflow_Flowrate = SingleValue("유입유량", 100, False, unit="m³/d")
    DEP.normal_count = SingleValue("상용대수", 2, True, unit="ea")
    DEP.Safety_Factor = SingleValue("여유율", 20.0, True, unit="%")

    # 3D 모델링 후 자동 생성된 Pipe 정보 (Unity에서 자동 전달)
    DEP.pipe_length = SingleValue("배관길이", 25.5, False, unit="m")
    DEP.tee_joint_count = SingleValue("T자 피팅", 3, False, unit="ea")
    DEP.elbow_count = SingleValue("엘보", 5, False, unit="ea")
    DEP.pipe_max_height = SingleValue("최대높이", 8.5, False, unit="m")
    DEP.pipe_min_height = SingleValue("최소높이", 1.2, False, unit="m")

    # === 2. 계산 로직 ===
    pump_capacity = (DEP.Inflow_Flowrate.value / DEP.normal_count.value) * \
                    (1 + DEP.Safety_Factor.value / 100)

    static_head = DEP.pipe_max_height.value - DEP.pipe_min_height.value

    friction_loss_per_m = 0.05  # m/m (예시값)
    fitting_loss = (DEP.tee_joint_count.value * 0.5) + \
                   (DEP.elbow_count.value * 0.3)

    total_friction_loss = (DEP.pipe_length.value * friction_loss_per_m) + fitting_loss

    total_head = static_head + total_friction_loss + 2.0  # +2m 여유

    # === 3. 결과 저장 (result) ===

    # Query 키 목록
    result.query = DropboxValue("query", ["pump_capacity", "total_head", "static_head", "friction_loss"], editable=False, display=False)
    # Param 키 목록
    result.param = DropboxValue("param", ["pump_capacity", "total_head", "static_head", "friction_loss"], editable=False, display=False)
    
    result.pump_capacity = SingleValue("펌프용량", round(pump_capacity, 2), editable=False, unit="m³/d·대", remark="대당 펌프 용량")
    result.total_head = SingleValue("전양정", round(total_head, 2), editable=False, unit="m", remark="정압 + 마찰손실 + 여유")
    result.static_head = SingleValue("정압", round(static_head, 2), editable=False, unit="m")
    result.friction_loss = SingleValue("마찰손실", round(total_friction_loss, 2), editable=False, unit="m")

    return result
```

---

## 추가 정보

### 시스템 요구사항

- **Python 버전**: 3.12 이상
- **Unity 연동**: `pythonnet` 라이브러리를 통한 직접 접근 지원

### 주요 기능

✅ **인스턴스별 데이터 분리**: Unity 오브젝트별 독립적인 설계 데이터 관리

✅ **체계적인 컨테이너 구조**: 용도별로 분류된 데이터 컨테이너

✅ **풍부한 값 타입**: 단일값, 범위값, 벡터, 공간 정보 등 다양한 데이터 타입 지원

✅ **메타 정보 관리**: 단위, 비고, 표시 옵션 등의 상세 정보 포함

✅ **계산식 프레임워크**: 규격/검증/수리 계산식의 표준화된 구조

✅ **3D 형상 관리**: Vector 및 Box 클래스를 통한 공간 데이터 관리

✅ **다중 단위계 지원**: METRIC, USCS 단위계 지원


### 문의

프로젝트에 대한 문의나 피드백은 담당자에게 전달해주세요.

---

**WAI v0.1.17** | © 2025 | [문서 버전: 2.3]
