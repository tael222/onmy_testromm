# oh-my-claudecode 플러그인 테스트 분석 리포트

> 작성일: 2026-01-28
> 작성 목적: OMC 플러그인의 실제 동작 양상 분석 및 효과 평가
> 테스트 환경: Claude Code + oh-my-claudecode v3.3.6~v3.7.2

---

## 1. 플러그인 개요

### 1.1 oh-my-claudecode (OMC)란

**oh-my-claudecode**는 Claude Code에 멀티 에이전트 오케스트레이션 레이어를 추가하는 플러그인입니다. oh-my-zsh가 셸의 복잡성을 추상화한 것처럼, Claude Code의 고급 기능을 제로 설정으로 사용할 수 있게 해줍니다.

### 1.2 핵심 아키텍처

```
┌──────────────────────────────────────────────────┐
│                  사용자 프롬프트                    │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│              OMC Hooks Layer                       │
│  (keyword-detector, skill-injector, session-start) │
└───────────────────────┬──────────────────────────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
        ┌──────────┐ ┌──────┐ ┌──────────┐
        │ 실행 계층 │ │향상  │ │ 보장 계층 │
        │ default  │ │계층  │ │  ralph   │
        │ planner  │ │ulw   │ │          │
        │orchestrate│ │tdd   │ │          │
        └────┬─────┘ └──┬───┘ └────┬─────┘
             └───────────┼─────────┘
                         ▼
              ┌─────────────────────┐
              │  32개 전문 에이전트   │
              │                     │
              │  HIGH  (Opus)       │
              │  ├─ architect       │
              │  ├─ planner        │
              │  └─ critic         │
              │                     │
              │  MEDIUM (Sonnet)    │
              │  ├─ executor       │
              │  ├─ designer       │
              │  └─ researcher     │
              │                     │
              │  LOW   (Haiku)      │
              │  ├─ explore        │
              │  └─ writer         │
              └─────────────────────┘
```

### 1.3 5가지 실행 모드

| 모드 | 속도 | 비용 | 특징 |
|------|------|------|------|
| Autopilot | 표준 | 표준 | 검증 완료까지 자동 진행 |
| Ultrapilot | 3-5x | 높음 | 최대 5개 워커 병렬 처리 |
| Ecomode | 표준 | 30-50% 절감 | 비용 최적화 모델 라우팅 |
| Swarm | 높음 | 높음 | 독립 작업 병렬 조율 |
| Pipeline | 표준 | 표준 | 순차적 멀티 스테이지 |

### 1.4 주요 스킬

| 분류 | 스킬 | 용도 |
|------|------|------|
| 실행 | ralph, autopilot, ultrawork | 작업 완료까지 자율 실행 |
| 계획 | plan, ralplan, ralph-init | 구조화된 계획 수립 |
| 검증 | ultraqa, code-review, security-review | 품질 보증 |
| 탐색 | deepsearch, analyze, research | 조사 및 분석 |

---

## 2. 테스트 설계

### 2.1 테스트 목적

OMC 플러그인이 실제 개발 작업에서 어떤 동작 양상을 보이는지, 그리고 명시적 스킬 호출 여부에 따라 효과가 어떻게 달라지는지 비교 분석합니다.

### 2.2 테스트 매트릭스

| 라운드 | PRD | 날짜 | 스킬 사용 | 목적 |
|--------|-----|------|----------|------|
| **1차** | Formula Checker | 2026-01-23 | 없음 (passive) | 스킬 미호출 시 플러그인 동작 관찰 |
| **2차-A** | ReadAlongBuddy Phase 1 | 2026-01-28 | ralph-init + ralph (active) | 명시적 스킬 사용 시 동작 비교 |
| **2차-B** | ReadAlongBuddy Phase 2+3 | 2026-01-28 | ralph-init + ralph 2차 (active) | 기존 코드 위 확장 구현, 대규모 병렬 실행 |

### 2.3 비교 축

```
             Passive (1차)         Active-A (2차-A)       Active-B (2차-B)
           ┌─────────────┐     ┌─────────────┐       ┌─────────────────┐
  스킬     │  미호출      │     │ ralph-init  │       │ ralph-init 2차  │
           │             │     │ ralph       │       │ ralph 2차       │
           └─────────────┘     └─────────────┘       └─────────────────┘
  에이전트  │  미호출      │     │ 4종 활용    │       │ 6종 활용         │
           │  (MAIN만)   │     │ exec, writer│       │ exec x3, exec-hi│
           │             │     │ architect   │       │ exec-lo, architect│
           └─────────────┘     └─────────────┘       └─────────────────┘
  병렬도   │  1 (순차)    │     │ 2 (병렬)    │       │ 5 (대규모 병렬)  │
           └─────────────┘     └─────────────┘       └─────────────────┘
```

---

## 3. 1차 테스트: Formula Checker (Passive 모드)

### 3.1 테스트 개요

| 항목 | 값 |
|------|-----|
| PRD | Formula Checker (WAI 모듈 기반 계산 스크립트 검증) |
| 플러그인 버전 | v3.3.6 |
| 스킬 사용 | 없음 |
| 에이전트 호출 | 없음 (MAIN만 사용) |
| 테스트 범위 | Test A(구현), B(피드백), C(수정방식), D(스킬분석) |

### 3.2 결과

| 항목 | 결과 |
|------|------|
| PRD 충족률 | 100% |
| 생성 파일 수 | 14개 (소스 7, 테스트 4, 설정/문서 3) |
| 코드 라인 수 | ~2,000 |
| 작업 패턴 | 사용자 요청 → MAIN 직접 구현 → 반복 |

### 3.3 관찰된 OMC 동작

| OMC 구성요소 | 동작 여부 | 관찰 내용 |
|-------------|----------|----------|
| **Hooks** | 동작함 | keyword-detector, skill-injector, session-start, stop-continuation 매 응답 실행 |
| **Skills** | 미동작 | 명시적 호출 없이 자동 활성화되지 않음 |
| **Agents** | 미동작 | Task tool로 에이전트 호출 없음, MAIN이 직접 구현 |
| **자동 감지** | 미동작 | keyword 기반 자동 트리거 발생하지 않음 |

### 3.4 핵심 발견

1. **스킬 미호출 시 OMC는 사실상 투명(transparent)**: 플러그인이 설치되어 있어도, 사용자가 스킬을 명시적으로 호출하지 않으면 hooks 외에는 동작하지 않음
2. **Hooks는 토큰 오버헤드만 발생**: 매 응답마다 system-reminder 주입으로 토큰을 소비하지만 기능적 효과 없음
3. **MAIN이 모든 작업을 직접 수행**: 오케스트레이터 패턴 미발동, 단일 AI 인스턴스와 동일한 동작

---

## 4. 2차 테스트: ReadAlongBuddy (Active 모드)

### 4.1 테스트 개요

| 항목 | 값 |
|------|-----|
| PRD | ReadAlongBuddy (Streamlit 웹앱, OCR + TTS) |
| 플러그인 버전 | v3.7.2 |
| 스킬 사용 | ralph-init (1회) + ralph (1회) |
| 에이전트 호출 | executor(2회), writer(1회), architect(1회) |
| 테스트 범위 | Phase 1 MVP (FR-001~004 + 비기능 요구사항) |

### 4.2 실행 흐름

```
[STEP-001] 테스트 환경 준비
  │  주체: MAIN
  │  스킬: 없음
  ▼
[STEP-002] ralph-init: PRD → User Story 분해
  │  주체: MAIN
  │  스킬: ralph-init
  │  결과: 7개 User Story + acceptance criteria
  ▼
[STEP-003] ralph 루프 진입
  │
  ├── [3a] 구현 위임 (병렬)
  │     주체: MAIN(오케스트레이터) → executor(Sonnet) + writer(Haiku)
  │     결과: 11개 파일 생성
  │
  ├── [3b] 문법 + 의존성 검증
  │     주체: MAIN
  │     결과: ALL PASS
  │
  ├── [3c] Architect 리뷰
  │     주체: architect(Opus)
  │     결과: 2건 이슈 발견 (TTS 속도, auto-TTS)
  │
  ├── [3d] 이슈 수정
  │     주체: executor(Sonnet)
  │     결과: 2파일 수정
  │
  └── [3e] 문법 재검증
        주체: MAIN
        결과: ALL PASS → 완료
```

### 4.3 에이전트 활용 분석

| 에이전트 | 모델 | 호출 수 | 실행 방식 | 역할 |
|---------|------|---------|----------|------|
| MAIN | Opus 4.5 | 상시 | 포그라운드 | 오케스트레이터 (코드 미작성) |
| executor | Sonnet | 2회 | 백그라운드 | 코드 구현 + 수정 |
| writer | Haiku | 1회 | 백그라운드 | README 문서 작성 |
| architect | Opus | 1회 | 포그라운드 | PRD 대조 검증, 이슈 발견 |

**모델 라우팅 패턴**:
- 코드 구현 → Sonnet (MEDIUM): 비용 효율적인 표준 구현
- 문서 작성 → Haiku (LOW): 가장 저렴한 티어로 단순 문서 작업
- 검증/리뷰 → Opus (HIGH): 가장 높은 추론 능력으로 정밀 검증

### 4.4 결과

| 항목 | 결과 |
|------|------|
| PRD 충족률 | 100% |
| 생성 파일 수 | 9개 (소스 5, 설정 3, 문서 1) |
| 코드 라인 수 | ~277 |
| Architect 발견 이슈 | 2건 (수정 완료) |
| Ralph 루프 단계 | 5단계 (구현→검증→리뷰→수정→재검증) |

### 4.5 핵심 발견

1. **ralph가 ultrawork를 자동 활성화**: 명시적으로 ultrawork를 호출하지 않았지만 ralph 스킬이 병렬 실행 모드를 자동으로 활성화함
2. **오케스트레이터 패턴 정상 발동**: MAIN이 직접 코드를 작성하지 않고 executor/writer에게만 위임하는 패턴이 동작함
3. **Architect 검증이 실질적 가치 제공**: gTTS API 한계(속도 옵션)와 UX 누락(OCR 후 자동 TTS)을 자동으로 발견
4. **자율적 수정-재검증 루프**: Architect 이슈 발견 → executor 수정 → 재검증까지 사용자 개입 없이 자동 진행

### 4.6 Phase 2+3 확장 테스트 (2차-B)

#### 4.6.1 테스트 개요

| 항목 | 값 |
|------|-----|
| PRD | ReadAlongBuddy Phase 2+3 (기존 Phase 1 위에 확장) |
| 플러그인 버전 | v3.7.2 |
| 스킬 사용 | ralph-init 2차 (1회) + ralph 2차 (1회) |
| 에이전트 호출 | executor(3회+수정1회), executor-high(1회), executor-low(1회), architect(1회) |
| 테스트 범위 | Phase 2 (FR-005~011) + Phase 3 (FR-012~016) = 13 User Stories |

#### 4.6.2 실행 흐름

```
[STEP-004] ralph-init 2차: Phase 2+3 PRD → 13 User Stories 분해
  │  주체: MAIN
  │  스킬: ralph-init
  │  결과: 13개 User Story (기존 Phase 1 완료 상태 위에 확장)
  ▼
[STEP-005] ralph 2차 루프 진입
  │
  ├── [5a] 5개 에이전트 병렬 위임 (ultrawork)
  │     ┌── Agent A (executor/Sonnet): Phase 2 신규 모듈 3개
  │     ├── Agent B (executor/Sonnet): 기존 모듈 수정 3개
  │     ├── Agent C (executor/Sonnet): Phase 3 신규 모듈 2개
  │     ├── Agent D (executor-low/Haiku): 설정 파일 업데이트 2개
  │     └── Agent E (executor-high/Opus): app.py 전체 재작성 (709줄)
  │     결과: 5신규 + 5수정 + 1재작성 = 11개 파일
  │
  ├── [5b] 문법 + 의존성 + import 검증
  │     주체: MAIN
  │     결과: ALL 9 FILES PASS
  │
  ├── [5c] Architect 리뷰
  │     주체: architect(Opus)
  │     결과: 1 CRITICAL + 4 MEDIUM + 6 LOW = 11건 이슈
  │
  ├── [5d] 이슈 수정 (수정 가능 4건)
  │     주체: executor(Sonnet)
  │     결과: 2파일 수정
  │
  └── [5e] 문법 재검증
        주체: MAIN
        결과: ALL PASS → 완료
```

#### 4.6.3 에이전트 활용 분석

| 에이전트 | 모델 | 호출 수 | 실행 방식 | 역할 |
|---------|------|---------|----------|------|
| MAIN | Opus 4.5 | 상시 | 포그라운드 | 오케스트레이터 (코드 미작성) |
| executor | Sonnet | 3회 | 백그라운드 병렬 | 모듈 구현 (신규 3+수정 3+Phase3 2) |
| executor-high | Opus | 1회 | 백그라운드 | app.py 전체 재작성 (709줄) |
| executor-low | Haiku | 1회 | 백그라운드 | 설정 파일 업데이트 |
| executor | Sonnet | 1회 | 포그라운드 | Architect 이슈 4건 수정 |
| architect | Opus | 1회 | 포그라운드 | PRD 대조 검증 (11건 이슈 발견) |

**Phase 1 대비 모델 라우팅 진화**:
- **Phase 1**: executor(Sonnet) + writer(Haiku) + architect(Opus) = 3종
- **Phase 2+3**: executor(Sonnet) x3 + executor-high(Opus) + executor-low(Haiku) + architect(Opus) = 6종
- **핵심 변화**: app.py 재작성 같은 복잡한 작업에 executor-high(Opus)를 사용하고, 설정 파일 같은 단순 작업에 executor-low(Haiku)를 사용하여 비용-복잡도 매핑이 더 세밀해짐

#### 4.6.4 Architect 검증 상세

Phase 2+3 Architect가 발견한 11건 이슈:

| # | 심각도 | 기능 | 이슈 | 근본 원인 |
|---|--------|------|------|----------|
| 1 | **CRITICAL** | FR-006 (STT) | Web Speech API 인식 텍스트가 Streamlit에 전달 불가 | Streamlit `components.html()` 단방향 통신 |
| 2 | Medium | FR-008 (하이라이트) | 정적 문장 하이라이트만 구현, 실시간 단어 동기화 없음 | Streamlit 서버 렌더링 모델 |
| 3 | Medium | FR-016 (연속 읽기) | 수동 버튼 클릭 필요, 자동 페이지 전환 불가 | Audio `ended` 이벤트 감지 불가 |
| 4 | Medium | FR-010 (히스토리) | "전체 보기" 텍스트가 다음 인터랙션에서 사라짐 | Streamlit rerun 모델 |
| 5 | Medium | FR-012 (PDF) | 다른 PDF 재업로드 시 기존 데이터 유지됨 | 상태 관리 로직 누락 |
| 6-11 | Low | 각종 | 대기시간 미설정, 반복 라벨, 점수 게이트 등 | UX 세부사항 |

**수정된 이슈 (4건)**: #4, #5, #10(truthiness 버그), 연속 읽기 UX 개선
**프레임워크 제약 (수정 불가)**: #1, #2, #3 - Streamlit의 서버 렌더링 아키텍처 근본 한계

#### 4.6.5 결과

| 항목 | Phase 1 | Phase 2+3 | 전체 |
|------|---------|-----------|------|
| User Stories | 7개 | 13개 | 20개 |
| 소스 코드 라인 | ~277줄 | +~1,255줄 | ~1,532줄 |
| PRD 충족률 | 100% (4/4) | 87% (11/13 PASS + 2 PARTIAL) | 14 PASS + 2 PARTIAL |
| Architect 이슈 | 2건 (전체 수정) | 11건 (4건 수정, 3건 프레임워크 제약) | 13건 |
| 병렬 에이전트 수 | 2개 | 5개 | - |
| Ralph 루프 단계 | 5단계 | 5단계 | 동일 패턴 |

#### 4.6.6 핵심 발견

1. **병렬도 확장**: Phase 1의 2개 에이전트에서 Phase 2+3는 5개 에이전트로 확장. ralph/ultrawork가 작업량에 따라 병렬도를 자동 조절
2. **모델 라우팅 세분화**: executor-high(Opus)를 복잡한 app.py 재작성에, executor-low(Haiku)를 단순 설정 파일에 배정하여 3티어 라우팅 활용
3. **기존 코드 보존 성공**: Phase 1의 4개 핵심 기능(FR-001~004)이 Phase 2+3 확장 후에도 모두 정상 동작 (Architect 확인)
4. **프레임워크 한계 노출**: Streamlit의 서버 렌더링 모델이 브라우저↔서버 양방향 이벤트(STT, 오디오 종료)를 지원하지 않아 일부 기능이 PARTIAL 상태
5. **Architect 검증 가치 증가**: Phase 1(2건) 대비 Phase 2+3(11건)으로 이슈 발견 건수 5.5배 증가. 복잡도가 높을수록 Architect 검증의 가치가 커짐
6. **수정-재검증 루프 동일 패턴**: Phase 1과 Phase 2+3 모두 구현→검증→Architect→수정→재검증의 5단계 루프를 동일하게 수행

---

## 5. 1차 vs 2차 비교 분석

### 5.1 동작 양상 비교

| 관점 | 1차 (Passive) | 2차 (Active) | 차이 |
|------|-------------|-------------|------|
| **작업 주체** | MAIN 단독 | MAIN + 3종 에이전트 | 멀티 에이전트 오케스트레이션 |
| **실행 패턴** | 순차적 단일 스레드 | 병렬 백그라운드 위임 | 동시 실행 |
| **품질 검증** | 없음 | Architect 자동 리뷰 | 자동 이슈 발견 |
| **수정 루프** | 수동 (사용자 피드백 필요) | 자동 (ralph 루프) | 자율적 개선 |
| **스킬 동작** | hooks만 (기능 없음) | ralph-init + ralph 활성 | 구조화된 실행 |
| **PRD 추적** | 없음 | prd.json + progress.txt | 체크리스트 기반 |

### 5.2 결과물 비교

| 항목 | 1차 (Formula Checker) | 2차-A (ReadAlongBuddy P1) | 2차-B (ReadAlongBuddy P2+3) |
|------|---------------------|--------------------------|---------------------------|
| PRD 충족률 | 100% | 100% | 87% (14 PASS + 2 PARTIAL) |
| 파일 수 | 14개 | 9개 | 14개 (5신규 + 9수정) |
| 코드 라인 | ~2,000 | ~277 | ~1,532 |
| 자동 검증 | 없음 | Architect (2건) | Architect (11건) |
| 수정 루프 | 수동 (Test B) | 자동 (ralph 내부) | 자동 (ralph 내부) |
| 에이전트 사용 | 0종 | 4종 | 6종 |
| 병렬 에이전트 | 0 | 2 | 5 |

> **참고**: 두 PRD의 규모와 복잡도가 다르므로 파일 수/코드량은 직접 비교 대상이 아닙니다. Formula Checker는 Python CLI 도구(7개 모듈), ReadAlongBuddy는 Streamlit 웹앱(3개 모듈)입니다.

### 5.3 OMC 동작 레벨 비교

```
           Passive (1차)          Active-A (2차-A)          Active-B (2차-B)

Level 5    ░░░░░░░░░░░░       ░░░░░░░░░░░░░░░░       ████████████████
           대규모 병렬             (미동작)                  5개 에이전트 동시 실행
           (미동작)                                        3티어 모델 라우팅

Level 4    ░░░░░░░░░░░░       ████████████████       ████████████████
           자율 루프              ralph 루프 동작           ralph 루프 동작
           (미동작)               (5단계)                   (5단계, 동일 패턴)

Level 3    ░░░░░░░░░░░░       ████████████████       ████████████████
           에이전트 위임           4종 에이전트              6종 에이전트
           (미동작)               (exec, writer, arch)     (exec x4, exec-lo, arch)

Level 2    ░░░░░░░░░░░░       ████████████████       ████████████████
           스킬 활성화            ralph-init + ralph       ralph-init + ralph (2차)
           (미동작)               (ultrawork 포함)          (ultrawork 포함)

Level 1    ████████████████   ████████████████       ████████████████
           Hooks 실행            Hooks 실행                Hooks 실행
```

---

## 6. 분석 결과

### 6.1 플러그인 활성화 조건

OMC 플러그인은 **명시적 트리거 없이는 Level 1(Hooks)에서만 동작**합니다. 상위 레벨 기능을 활성화하려면 다음 중 하나가 필요합니다:

| 활성화 방법 | 예시 | 효과 |
|------------|------|------|
| 슬래시 커맨드 | `/oh-my-claudecode:ralph` | 해당 스킬 직접 실행 |
| 매직 키워드 | "ralph: 이 기능 구현해줘" | 키워드 감지 → 스킬 자동 활성화 |
| 자동 감지 | 복잡한 작업 요청 | (이론상 가능, 1차 테스트에서는 미발동) |

### 6.2 Ralph 스킬의 효과

ralph를 통해 활성화된 주요 메커니즘:

1. **오케스트레이터 패턴**: MAIN이 코드를 직접 작성하지 않고 전문 에이전트에게 위임
2. **ultrawork 자동 활성화**: 병렬 백그라운드 실행으로 executor + writer 동시 작업
3. **Architect 필수 검증**: 완료 선언 전 Opus 레벨의 코드 리뷰 강제
4. **자율적 수정 루프**: 이슈 발견 시 사용자 개입 없이 자동 수정 + 재검증
5. **PRD 추적**: prd.json 기반 User Story 체크리스트로 누락 방지
6. **적응적 병렬도**: 작업량에 따라 병렬 에이전트 수를 자동 조절 (2차-A: 2개 → 2차-B: 5개)
7. **3티어 모델 라우팅**: 작업 복잡도에 따라 Haiku(단순)/Sonnet(표준)/Opus(복잡) 자동 배정

### 6.3 Architect 검증의 가치

2차 테스트에서 Architect(Opus)가 발견한 2건의 이슈:

| 이슈 | 심각도 | 내용 | 발견 가능성 (수동) |
|------|--------|------|-------------------|
| gTTS 속도 한계 | Medium | "빠르게"와 "보통"이 동일 출력 → JS playbackRate로 해결 | 테스트 시 발견 가능 |
| OCR 후 auto-TTS 누락 | Low | PRD 시나리오 6.1과 불일치 → auto-trigger 추가 | PRD 대조 시 발견 가능 |

두 이슈 모두 기능 테스트나 PRD 대조 시 발견 가능한 수준이지만, **코드 작성 직후 자동으로 발견했다는 점**이 핵심입니다. 수동 리뷰가 필요 없었습니다.

**Phase 2+3 Architect 검증 (2차-B):**

| 이슈 | 심각도 | 내용 | 유형 |
|------|--------|------|------|
| STT 단방향 통신 | CRITICAL | components.html()로 JS→Python 데이터 전달 불가 | 프레임워크 제약 |
| 정적 하이라이트 | Medium | 실시간 단어 동기화 미구현 | 프레임워크 제약 |
| 수동 연속 읽기 | Medium | 오디오 종료 이벤트 감지 불가 | 프레임워크 제약 |
| 히스토리 UI 임시성 | Medium | Streamlit rerun으로 UI 상태 소실 | 수정 완료 |
| PDF 재업로드 | Medium | 상태 관리 누락 | 수정 완료 |
| 기타 6건 | Low | UX 세부사항 | 1건 수정, 5건 유지 |

**핵심 관찰**: Architect가 **프레임워크 수준의 근본적 한계**까지 식별함. 이는 단순한 버그 발견을 넘어 기술 선택에 대한 아키텍처 리뷰의 가치를 보여줌. Streamlit의 서버 렌더링 모델이 STT, 실시간 오디오 이벤트 등 브라우저 네이티브 기능과 호환되지 않는다는 점을 정확히 지적함.

### 6.4 모델 라우팅 비용 효과

2차 테스트에서 관찰된 모델 라우팅:

```
작업 유형별 모델 배정:
  문서 작성 (README)     → Haiku  (LOW)    : 가장 저렴
  코드 구현 (app, modules) → Sonnet (MEDIUM) : 비용-성능 균형
  검증 리뷰 (Architect)   → Opus   (HIGH)   : 최고 추론 능력
```

이 라우팅은 ralph/ultrawork가 자동으로 결정한 것으로, 동일한 작업을 Opus 단일 모델로 수행하는 것 대비 비용 절감 효과가 있습니다. 다만 정확한 토큰 절감률은 without-omc 대조 테스트 후 측정 가능합니다.

---

## 7. 주요 발견 사항 요약

### 7.1 확인된 사실

| # | 발견 사항 | 근거 |
|---|----------|------|
| 1 | **스킬 미호출 시 OMC는 hooks 외에 동작하지 않음** | 1차 테스트: 에이전트/스킬 모두 미동작 |
| 2 | **ralph 호출 시 ultrawork가 자동 활성화됨** | 2차 테스트: 병렬 백그라운드 실행 자동 발동 |
| 3 | **오케스트레이터 패턴이 실제로 동작함** | 2차 테스트: MAIN이 코드 미작성, executor에게만 위임 |
| 4 | **Architect 검증이 실질적 이슈를 발견함** | 2차 테스트: 2건의 기능/UX 이슈 자동 발견 |
| 5 | **자율적 수정-재검증 루프가 작동함** | 2차 테스트: 이슈 발견→수정→재검증까지 자동 |
| 6 | **모델 라우팅이 작업 유형별로 차등 적용됨** | 2차 테스트: Haiku(문서), Sonnet(코드), Opus(검증) |
| 7 | **병렬도가 작업량에 따라 자동 확장됨** | 2차-B: Phase 1의 2개 → Phase 2+3의 5개 에이전트 |
| 8 | **모델 라우팅이 3티어로 세분화됨** | 2차-B: executor-low(Haiku), executor(Sonnet), executor-high(Opus) |
| 9 | **기존 코드 위 확장 구현이 성공적으로 동작함** | 2차-B: Phase 1 기능 전체 보존 (Architect 확인) |
| 10 | **Architect가 프레임워크 수준 제약도 식별함** | 2차-B: Streamlit 서버 렌더링 모델의 근본 한계 지적 |
| 11 | **복잡도 증가 시 Architect 가치가 비례 증가** | 2차-A: 2건 → 2차-B: 11건 (5.5배) |

### 7.2 미확인 사항 (추가 테스트 필요)

| # | 미확인 사항 | 필요한 테스트 |
|---|-----------|-------------|
| 1 | 토큰 사용량 차이 (with-omc vs without-omc) | without-omc 동일 PRD 테스트 |
| 2 | 실제 비용 절감률 | 토큰 사용량 비교 |
| 3 | 매직 키워드 자동 감지 동작 여부 | 키워드 포함 프롬프트 테스트 |
| 4 | ~~복잡도에 따른 효과 차이~~ | ✅ **확인됨** (2차-B): 복잡도 증가 시 병렬도↑, Architect 이슈↑ |
| 5 | ecomode, swarm, pipeline 모드 효과 | 개별 모드 테스트 |
| 6 | 기존 코드 위 확장 시 안정성 | ✅ **확인됨** (2차-B): Phase 1 전체 보존 성공 |

---

## 8. 결론 및 권고

### 8.1 결론

oh-my-claudecode 플러그인은 **"설치만 하면 자동으로 동작하는 도구"가 아니라, "명시적으로 호출했을 때 강력한 오케스트레이션을 제공하는 도구"**입니다.

- **Passive 모드**: Hooks만 동작하여 토큰 오버헤드만 발생. 바닐라 Claude Code와 실질적 차이 없음.
- **Active 모드(ralph)**: 멀티 에이전트 오케스트레이션, 병렬 실행, 자동 품질 검증, 자율 수정 루프가 모두 정상 동작. 단일 AI 인스턴스 대비 구조화된 개발 프로세스 제공.

핵심 가치는 **"사용자가 스킬을 호출한 순간"** 발현됩니다. ralph/ultrawork 같은 스킬을 통해 자동 위임, 병렬 처리, Architect 검증이라는 워크플로우가 활성화되며, 이는 수동 개발 대비 품질 보증과 자율성 측면에서 명확한 이점을 제공합니다.

Phase 2+3 확장 테스트(2차-B)에서 추가로 확인된 사항:
- **적응적 스케일링**: 작업 규모가 커지면 병렬 에이전트 수와 모델 라우팅이 자동으로 정교해짐 (2→5 에이전트, 2→3 티어)
- **Architect 가치 비례 증가**: 코드 복잡도가 높을수록 자동 검증의 가치가 급격히 증가 (2건→11건)
- **기존 코드 안전 확장**: Phase 1 기능을 보존하면서 Phase 2+3를 성공적으로 확장하여, ralph의 점진적 개발 지원 능력 확인
- **프레임워크 한계 인식**: Architect가 구현 버그뿐 아니라 기술 스택의 근본적 한계(Streamlit 서버 렌더링)까지 식별하여 아키텍처 수준의 의사결정 지원

### 8.2 다음 단계 권고

| 우선순위 | 테스트 | 목적 |
|---------|--------|------|
| **P0** | without-omc ReadAlongBuddy 구현 | 동일 PRD로 토큰/품질 직접 비교 |
| **P1** | 매직 키워드 테스트 | "ralph: 구현해줘" 형태의 자동 감지 확인 |
| **P2** | ecomode 테스트 | 비용 절감 효과 정량적 측정 |
| **P3** | 대규모 PRD 테스트 | 복잡도 증가 시 플러그인 효과 확대 여부 |

---

## Appendix A: 테스트 파일 위치

```
workplace/
├── analysis_report.md          ← 본 문서
├── comparison.md               ← 테스트 비교 요약
├── with-omc/
│   ├── test-a-20260123/        ← 1차 테스트 (Formula Checker, Passive)
│   │   ├── formula_checker/    (소스 코드)
│   │   ├── tests/              (테스트 코드)
│   │   ├── metrics.md          (메트릭)
│   │   ├── test_b_c_analysis.md
│   │   └── test_d_skill_analysis.md
│   └── test-buddy-20260128/    ← 2차 테스트 (ReadAlongBuddy, Active)
│       ├── app.py              (Streamlit 앱 - 709줄, Phase 1+2+3)
│       ├── modules/
│       │   ├── ocr.py          (OCR - 한글 지원)
│       │   ├── tts.py          (TTS - 한글 + 음성 선택)
│       │   ├── ui.py           (UI - Phase 2+3 CSS)
│       │   ├── reading_mode.py (따라 읽기 - 문장 분리/하이라이트)
│       │   ├── stt.py          (STT - Web Speech API)
│       │   ├── pronunciation.py(발음 교정 피드백)
│       │   ├── pdf_handler.py  (PDF 페이지 추출)
│       │   └── book_manager.py (책 관리/라이브러리)
│       ├── execution_log.md    (실행 로그 - Phase 1+2+3)
│       └── metrics.md          (메트릭 - Phase 1+2+3)
└── without-omc/
    └── test-a-20260123/        ← without-omc 비교 (미완료)
```

## Appendix B: 2차 테스트 에이전트 호출 상세

| 단계 | 에이전트 | 모델 | subagent_type | 실행 방식 | 입력 | 출력 |
|------|---------|------|--------------|----------|------|------|
| 3a | executor | Sonnet | oh-my-claudecode:executor | background | US-001~006 요구사항 | 8개 파일 생성 |
| 3a | writer | Haiku | oh-my-claudecode:writer | background | README 요구사항 | README.md |
| 3c | architect | Opus | oh-my-claudecode:architect | foreground | 전체 소스 + PRD | 2건 이슈 리포트 |
| 3d | executor | Sonnet | oh-my-claudecode:executor | foreground | Architect 이슈 2건 | tts.py, app.py 수정 |

### Phase 2+3 에이전트 호출 상세

| 단계 | 에이전트 | 모델 | subagent_type | 실행 방식 | 입력 | 출력 |
|------|---------|------|--------------|----------|------|------|
| 5a-A | executor | Sonnet | oh-my-claudecode:executor | background | Phase 2 모듈 설계 | reading_mode.py, stt.py, pronunciation.py |
| 5a-B | executor | Sonnet | oh-my-claudecode:executor | background | 기존 모듈 수정 | ocr.py, tts.py, ui.py 수정 |
| 5a-C | executor | Sonnet | oh-my-claudecode:executor | background | Phase 3 모듈 설계 | pdf_handler.py, book_manager.py |
| 5a-D | executor-low | Haiku | oh-my-claudecode:executor-low | background | 의존성 업데이트 | requirements.txt, packages.txt |
| 5a-E | executor-high | Opus | oh-my-claudecode:executor-high | background | Phase 1+2+3 통합 | app.py (709줄 재작성) |
| 5c | architect | Opus | oh-my-claudecode:architect | foreground | 전체 소스 + PRD | 11건 이슈 리포트 |
| 5d | executor | Sonnet | oh-my-claudecode:executor | foreground | 수정 가능 4건 | app.py, book_manager.py 수정 |
