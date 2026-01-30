# onmy_testromm: oh-my-claudecode 플러그인 효과 비교 테스트

**oh-my-claudecode** 플러그인이 Claude Code의 개발 생산성에 미치는 영향을 정량적/정성적으로 분석하기 위한 테스트 환경입니다.
동일한 PRD(Product Requirements Document)를 기반으로 플러그인 적용(`with-omc`)과 미적용(`without-omc`) 조건에서 각각 구현을 수행하고, 토큰 사용량, 코드 품질, 작업 방식 등을 비교합니다.

## 목차

- [테스트 방법론](#테스트-방법론)
- [디렉토리 구조](#디렉토리-구조)
- [테스트 과제: Formula Checker](#테스트-과제-formula-checker)
- [테스트 시나리오](#테스트-시나리오)
- [평가 기준](#평가-기준)
- [테스트 실행 방법](#테스트-실행-방법)
- [현재 진행 상황](#현재-진행-상황)
- [참고 문서](#참고-문서)

---

## 테스트 방법론

### 비교 구조

```
동일한 PRD (docs/PRD.md)
         │
    ┌────┴────┐
    ▼         ▼
with-omc   without-omc
(플러그인 O)  (플러그인 X)
    │         │
    ▼         ▼
 구현 결과   구현 결과
    │         │
    └────┬────┘
         ▼
    비교 분석 (comparison.md)
```

- **통제 변수**: PRD 문서, WAI 모듈 문서, Claude Code 버전
- **독립 변수**: oh-my-claudecode 플러그인 활성화 여부
- **종속 변수**: 토큰 사용량, 코드 완성도, 작업 방식, skill 활용도

### oh-my-claudecode 플러그인

| 항목 | 내용 |
|------|------|
| 버전 | v3.3.6 |
| Skills | 32개 (`/plan`, `/ralph`, `/ultrawork`, `/tdd` 등) |
| Agents | 32개 (analyst, architect, executor, critic 등) |
| Hooks | 6개 (keyword-detector, skill-injector, session-start 등) |
| Magic Keywords | `ralph`, `ulw`, `plan`, `autopilot` 등 자동 활성화 |

플러그인 상세 분석: `docs/ENVIRONMENT_ANALYSIS.md`

---

## 디렉토리 구조

```
onmy_testromm/
├── docs/                              # 참조 문서 (READ-ONLY, 테스트 간 공유)
│   ├── PRD.md                         # 구현 과제 명세서 (Formula Checker)
│   ├── pythonWAI_README.md            # WAI 모듈 API 문서
│   ├── TEST_PLAN.md                   # 테스트 계획서
│   └── ENVIRONMENT_ANALYSIS.md        # 플러그인 환경 분석
│
├── workplace/                         # 테스트 실행 결과
│   ├── with-omc/                      # 플러그인 적용 테스트
│   │   └── test-a-20260123/           # Test A 결과 (타임스탬프별 격리)
│   │       ├── formula_checker/       # 구현된 소스 코드
│   │       ├── tests/                 # 테스트 코드
│   │       ├── pyproject.toml
│   │       ├── README.md
│   │       └── metrics.md             # 토큰 사용량 기록
│   │
│   ├── without-omc/                   # 플러그인 미적용 테스트
│   │   └── test-a-{timestamp}/        # (별도 세션에서 실행)
│   │
│   └── comparison.md                  # 비교 분석 결과 집계
│
├── CLAUDE.md                          # Claude Code 가이드라인
└── README.md                          # 이 문서
```

**핵심 규칙**:
1. `docs/` 내 파일은 절대 수정하지 않음 (양쪽 테스트에서 동일 조건 보장)
2. 각 테스트는 `workplace/{with|without}-omc/test-{id}-{timestamp}/` 아래 격리 실행
3. 양쪽 모두 `docs/PRD.md` 명세를 그대로 따라 구현

---

## 테스트 과제: Formula Checker

양쪽 테스트에서 동일하게 구현하는 과제는 **WAI 계산식 검증 도구**입니다.

### 과제 개요

Unity 환경 없이 WAI 기반 Python 계산식(Process / Structure / Equipment)의 문법 검증, 함수 정의 확인, 컨테이너 사용 검증, `exec()` 기반 통합 테스트를 수행하는 내부 CLI 도구.

### 요구 기능 (PRD 기준)

| 기능 | 설명 |
|------|------|
| 문법 검사 | Python 3.12+ AST 기반 구문 검증 |
| 함수 정의 검증 | Structure(`forward/reverse/level_calculate`), Equipment(`forward_calculate`) |
| 컨테이너 검증 | DCN, DCR, DCP, DSP, DEP 등 WAI 컨테이너의 ValueObject 타입 적합성 |
| 통합 테스트 | `exec()` 기반 공정→구조물→기계설비 계산식 조합 실행 재현 |
| 입출력 제어 | Unity 없이 설계 조건 수동 정의 및 결과 확인 |

상세 요구사항: `docs/PRD.md`
WAI 모듈 API: `docs/pythonWAI_README.md`

---

## 테스트 시나리오

### Test A: 프로젝트 완성 일괄 실행

PRD 기반으로 Formula Checker를 처음부터 완성합니다.

| 단계 | 작업 | 측정 항목 |
|------|------|----------|
| A-1 | 프로젝트 구조 설계 | 토큰, 코드량 |
| A-2 | 핵심 기능 구현 | 토큰, 파일 수 |
| A-3 | 테스트 작성 | 토큰, 커버리지 |
| A-4 | 문서화 | 토큰, 문서 품질 |

### Test B: Feedback 반영

완성된 프로젝트에 변경 요청(기능 추가, 버그 수정, 리팩토링, 스펙 변경)을 반영합니다.

### Test C: 반영 방식 분석

변경 요청 시 **부분 수정 vs 전체 재시작** 중 어떤 전략을 사용하는지 분석합니다.
- 기존 코드 분석 여부
- 영향 범위 파악 정도
- 의존성 자동 처리 여부

### Test D: Skill 사용 분석

oh-my-claudecode가 제공하는 skill(`/plan`, `/ralph`, `/tdd`, `/ultrawork` 등)의 실제 활용도를 분석합니다.

상세 테스트 계획: `docs/TEST_PLAN.md`

---

## 평가 기준

### 정량 지표

| 지표 | 설명 | 가중치 |
|------|------|--------|
| 토큰 효율성 | 동일 결과물 대비 토큰 사용량 | 30% |
| 완성도 | PRD 요구사항 충족률 | 25% |
| 코드 품질 | 린트, 타입 오류, 테스트 커버리지 | 20% |
| 반영 속도 | Feedback 반영에 필요한 토큰/턴 수 | 15% |
| 정확성 | 불필요한 재작업 발생 빈도 | 10% |

### 정성 지표

- 워크플로우 자연스러움
- 에러 복구 능력
- 컨텍스트 유지력
- 사용자 개입 필요 빈도

---

## 테스트 실행 방법

### 1. 사전 준비

```bash
git clone <repo-url>
cd onmy_testromm
```

### 2. with-omc 테스트 (플러그인 활성화)

oh-my-claudecode 플러그인이 활성화된 상태에서 Claude Code 세션을 시작하고, PRD 기반 구현을 수행합니다.

```
# Claude Code 세션에서:
# 1. docs/PRD.md 참조하여 Formula Checker 구현
# 2. workplace/with-omc/test-a-{timestamp}/ 아래에 결과물 생성
# 3. 세션 종료 시 /cost로 토큰 사용량 기록 → metrics.md
```

### 3. without-omc 테스트 (플러그인 비활성화)

```jsonc
// ~/.claude/settings.json 에서 플러그인 비활성화
{
  "enabledPlugins": {
    "oh-my-claudecode@omc": false
  }
}
```

새 세션에서 동일한 PRD 기반 구현을 수행합니다.

```
# Claude Code 세션에서:
# 1. 동일하게 docs/PRD.md 참조하여 구현
# 2. workplace/without-omc/test-a-{timestamp}/ 아래에 결과물 생성
# 3. 세션 종료 시 /cost로 토큰 사용량 기록 → metrics.md
```

### 4. 토큰 기록

각 테스트 완료 후 `metrics.md`에 기록:

```markdown
## Test Metrics
- Date: YYYY-MM-DD
- Plugin: with-omc / without-omc
- Input tokens: XXX
- Output tokens: XXX
- Total tokens: XXX
- Task completion: Yes/No
- Notes: [관찰 사항]
```

### 5. 비교 분석

`workplace/comparison.md`에 양쪽 결과를 집계하여 비교합니다.

---

## 현재 진행 상황

| 테스트 | 플러그인 | 상태 | 파일 수 | 비고 |
|--------|---------|------|---------|------|
| Test A | with-omc | 완료 | 14 | PRD 100% 충족 |
| Test B | with-omc | 완료 | +1 | JSON 내보내기/비교 기능 추가 |
| Test C | with-omc | 완료 | - | 부분 수정 방식 사용 확인 |
| Test D | with-omc | 완료 | - | 명시적 skill 사용 없음, hooks만 동작 |
| Test A | without-omc | 대기 | - | 별도 세션 필요 |

### with-omc 주요 관찰 사항

1. 명시적 skill 호출 없이 일반 구현 작업 완료
2. system-reminder hook이 매 응답마다 동작
3. keyword 기반 자동 활성화 트리거 미발생
4. 플러그인 효과는 복잡한 계획 수립/병렬 작업 시 더 두드러질 것으로 예상

---

## 참고 문서

| 문서 | 경로 | 설명 |
|------|------|------|
| PRD | `docs/PRD.md` | Formula Checker 요구사항 명세 |
| WAI 모듈 문서 | `docs/pythonWAI_README.md` | WAI API 레퍼런스 (1,500+ lines) |
| 테스트 계획서 | `docs/TEST_PLAN.md` | 4개 시나리오 상세 계획 |
| 환경 분석 | `docs/ENVIRONMENT_ANALYSIS.md` | oh-my-claudecode 기능 목록 및 분석 |
| 비교 결과 | `workplace/comparison.md` | 테스트 결과 비교 집계 |
