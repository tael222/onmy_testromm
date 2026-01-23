# Formula Checker

WAI 계산식 검증 도구 - Unity 환경 없이 계산식 검증 및 실행 재현

## 개요

이 도구는 Python 기반 계산 지원 모듈(WAI)을 사용하여 작성된 계산식이 내부 규칙에 맞게 구현되었는지 검증하고, Unity 환경 없이도 계산 결과를 재현·분석할 수 있습니다.

## 요구사항

- Python 3.12 이상

## 설치

```bash
pip install -e .
```

## 사용법

### 전체 검사

```bash
formula-checker check path/to/formula.py
```

### 문법 검사

```bash
formula-checker syntax path/to/formula.py
formula-checker syntax path/to/directory -d  # 디렉토리 전체
```

### 함수 정의 검증

```bash
formula-checker function path/to/formula.py -t structure
formula-checker function path/to/formula.py -t equipment
formula-checker function path/to/formula.py -t process
```

### 컨테이너 사용 검증

```bash
formula-checker container path/to/formula.py -v
```

### 통합 테스트

```bash
formula-checker integration process.py -s structure1.py structure2.py -e equipment1.py
formula-checker integration process.py -i inputs.json -o result.json
```

## 모듈 구조

```
formula_checker/
├── __init__.py          # 패키지 초기화
├── syntax_checker.py    # 문법 검사
├── function_validator.py # 함수 정의 검증
├── container_validator.py # 컨테이너 사용 검증
├── integration_runner.py  # exec 기반 통합 테스트
├── input_controller.py    # 입출력 제어
└── cli.py               # 명령줄 인터페이스
```

## 기능

### 1. 개별 계산식 단독 검증

- Python 문법 오류 검사 (Python 3.12+ 기준)
- 필수 함수 정의 여부 확인
  - Structure: `forward_calculate`, `reverse_calculate`, `level_calculate`
  - Equipment: `forward_calculate`
- 컨테이너 사용성 점검 (DCN, DCR, DCP, DSP, DEP 등)

### 2. 통합 테스트

- exec() 실행 재현
- 공정 → 구조물 → 기계설비 연쇄 계산
- 데이터 흐름 및 상태 유지 검증

### 3. 입출력 제어

- 입력값 수동 설정 (JSON 파일 지원)
- 중간값 및 결과 출력
- 오류 위치 추적

## 테스트 실행

```bash
pytest tests/ -v
```

## 라이선스

MIT
