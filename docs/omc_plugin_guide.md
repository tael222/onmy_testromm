# oh-my-claudecode (OMC) 플러그인 종합 가이드

> 작성일: 2026-01-28
> 버전 기준: v3.7.2
> 목적: 플러그인 특징 정리 및 테스트 참고용

---

## 1. 개요

**oh-my-claudecode (OMC)**는 Claude Code를 위한 멀티 에이전트 오케스트레이션 플러그인입니다.

핵심 철학: *"Claude Code를 배우지 마세요. 그냥 OMC를 사용하세요."*

oh-my-zsh가 쉘의 복잡성을 추상화한 것처럼, OMC는 Claude Code의 고급 기능을 제로 설정으로 제공합니다. 단일 AI 인스턴스로 작동하는 바닐라 Claude Code와 달리, **32개의 전문화된 에이전트**를 자동으로 오케스트레이션하여 각 작업에 최적화된 전문가를 투입합니다.

### 핵심 수치
- 전문 에이전트: 32개
- 스킬: 35개+
- 실행 모드: 5가지
- GitHub Stars: 3,100+

---

## 2. 5가지 실행 모드

| 모드 | 설명 | 특징 |
|------|------|------|
| **Autopilot** | 완전 자율 실행 | 표준 속도, 검증 완료까지 자동 진행 |
| **Ultrapilot** | 최대 병렬 처리 | 3-5배 빠른 실행, 최대 5개 동시 워커 |
| **Ecomode** | 예산 최적화 | 30-50% 토큰 절감 |
| **Swarm** | 독립 작업 병렬 조율 | 동시 다발적 독립 작업 처리 |
| **Pipeline** | 순차적 멀티 스테이지 | 단계별 의존성이 있는 작업 |

---

## 3. 아키텍처

### 3.1 3계층 스킬 구성

```
[실행 스킬] + [0-N개 향상 스킬] + [선택적 보장 스킬]
```

1. **실행 계층**: 주요 작업 핸들러 (default, planner, orchestrate)
2. **향상 계층**: 선택적 역량 스택 (ultrawork, git-master, frontend-ui-ux 등)
3. **보장 계층**: 완료 강제 (ralph 스킬)

### 3.2 에이전트 티어 구조

| 티어 | 모델 | 용도 |
|------|------|------|
| LOW | Claude Haiku | 빠른 조회, 단순 작업 |
| MEDIUM | Claude Sonnet | 표준 구현, 일반 개발 |
| HIGH | Claude Opus | 복잡한 추론, 아키텍처 결정 |

작업 복잡도에 따라 자동으로 모델이 선택되어 비용 효율성을 극대화합니다.

### 3.3 검증 프로토콜

작업 완료 시 표준화된 검증 수행:
- BUILD, TEST, LINT, FUNCTIONALITY 자동 확인
- ARCHITECT 리뷰, TODO 완료, ERROR_FREE 상태 점검
- 증거는 5분 이내 최신이어야 하며 실제 명령어 출력 포함 필수

---

## 4. 32개 전문 에이전트

### 도메인별 에이전트 매트릭스

| 도메인 | LOW (Haiku) | MEDIUM (Sonnet) | HIGH (Opus) |
|--------|-------------|-----------------|-------------|
| 아키텍처 | architect-low | architect-medium | **architect** |
| 실행 | executor-low | **executor** | executor-high |
| 검색 | **explore** | explore-medium | explore-high |
| 연구 | researcher-low | **researcher** | — |
| 프론트엔드 | designer-low | **designer** | designer-high |
| 문서화 | **writer** | — | — |
| 비주얼 분석 | — | **vision** | — |
| 계획 | — | — | **planner** |
| 비평 | — | — | **critic** |
| QA | — | **qa-tester** | qa-tester-high |
| 보안 | security-reviewer-low | — | **security-reviewer** |
| 빌드 | build-fixer-low | **build-fixer** | — |
| TDD | tdd-guide-low | **tdd-guide** | — |
| 코드 리뷰 | code-reviewer-low | — | **code-reviewer** |
| 데이터 과학 | scientist-low | **scientist** | scientist-high |

### 핵심 에이전트 12종

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| **architect** | Opus | 아키텍처 설계, 디버깅, 근본 원인 조사 |
| **planner** | Opus | 인터뷰 스타일 전략 계획 |
| **critic** | Opus | 계획의 비판적 평가 |
| **analyst** | Opus | 사전 계획, 숨겨진 요구사항 식별 |
| **executor** | Sonnet | 직접 작업 구현 |
| **designer** | Sonnet | UI/UX 컴포넌트 설계 |
| **researcher** | Sonnet | 문서화, 다중 리포지토리 분석 |
| **vision** | Sonnet | 스크린샷, 다이어그램 해석 |
| **qa-tester** | Sonnet | tmux 기반 대화형 테스팅 |
| **scientist** | Sonnet | 데이터 분석, 연구 실행 |
| **explore** | Haiku | 빠른 코드베이스 패턴 매칭 |
| **writer** | Haiku | README, API 문서 작성 |

---

## 5. 매직 키워드 및 자동 동작

### 5.1 매직 키워드

자연어 프롬프트에 포함하여 명시적으로 모드를 활성화할 수 있습니다:

| 키워드 | 효과 | 사용 예시 |
|--------|------|----------|
| **autopilot:** | 자율 실행 | "autopilot: 이 기능 구현해줘" |
| **ralph:** | 지속성 모드 (포기하지 않음) | "ralph: 모든 버그 수정해줘" |
| **ulw** | 최대 병렬 처리 | "ulw API 리팩토링" |
| **eco:** | 토큰 효율 모드 | "eco: 단위 테스트 작성" |
| **plan** | 계획 인터뷰 시작 | "plan 새 엔드포인트 설계" |

**조합 가능**: `ralph ulw: 데이터베이스 마이그레이션 수행`

### 5.2 자동 감지 동작

| 사용자 행동 | 자동 동작 |
|-------------|-----------|
| 복잡한 작업 요청 | 전문 에이전트 병렬 위임 |
| 계획 요청 | 인터뷰식 계획 세션 시작 |
| 완전한 구현 요청 | 검증 완료까지 자동 지속 |
| UI/프론트엔드 작업 | 디자인 감각 활성화 |
| "stop" / "cancel" | 현재 작업 지능적 중단 |

---

## 6. 주요 스킬 (슬래시 커맨드)

### 핵심 스킬

| 스킬 | 설명 |
|------|------|
| `/oh-my-claudecode:autopilot` | 완전 자율 실행 |
| `/oh-my-claudecode:ultrawork` | 병렬 에이전트 오케스트레이션 (최대 5워커) |
| `/oh-my-claudecode:ralph` | 자기 참조 루프 - 완료까지 지속 |
| `/oh-my-claudecode:ralph-init` | PRD 기반 구조화된 실행 초기화 |
| `/oh-my-claudecode:plan` | 인터뷰식 계획 세션 |
| `/oh-my-claudecode:ralplan` | Planner + Architect + Critic 반복 계획 |
| `/oh-my-claudecode:ultraqa` | 자율 QA 사이클링 (테스트-검증-수정 반복) |
| `/oh-my-claudecode:analyze` | 심층 조사 및 분석 |
| `/oh-my-claudecode:deepsearch` | 다중 전략 코드베이스 검색 |
| `/oh-my-claudecode:research` | 병렬 과학자 에이전트 오케스트레이션 |

### 향상 스킬

| 스킬 | 설명 |
|------|------|
| `/oh-my-claudecode:deepinit` | 계층적 코드베이스 문서화 (AGENTS.md) |
| `/oh-my-claudecode:tdd` | 테스트 우선 개발 강제 |
| `/oh-my-claudecode:frontend-ui-ux` | 디자이너-개발자 모드 |
| `/oh-my-claudecode:git-master` | Git 전문가 모드 |
| `/oh-my-claudecode:learner` | 재사용 가능한 스킬 추출 |
| `/oh-my-claudecode:code-review` | 종합 코드 리뷰 |
| `/oh-my-claudecode:security-review` | 보안 취약점 검사 |

### 유틸리티 스킬

| 스킬 | 설명 |
|------|------|
| `/oh-my-claudecode:omc-setup` | 초기 설정 (유일하게 필수) |
| `/oh-my-claudecode:doctor` | 문제 진단 |
| `/oh-my-claudecode:help` | 사용 가이드 |
| `/oh-my-claudecode:hud` | 상태 표시줄 설정 |
| `/oh-my-claudecode:note` | notepad.md에 노트 저장 |

---

## 7. 핵심 시스템

### Notepad Wisdom System
- `.omc/notepads/{plan-name}/`에 계획 범위 지식 자동 캡처
- 학습, 결정, 이슈, 문제를 4개 마크다운 파일로 관리

### Real-Time HUD
- 상태 표시줄에 오케스트레이션 메트릭 실시간 표시
- 활성 에이전트, 토큰 사용량, 진행 상황 모니터링

### Skill Extraction
- 완료된 세션에서 문제 해결 패턴 자동 분석
- 재사용 가능한 스킬로 추출하여 향후 세션에 적용

### Analytics & Cost Tracking
- 세션 전반의 토큰 사용 추세 추적
- 작업당 비용 종합 대시보드

---

## 8. 바닐라 Claude Code 대비 차이점

| 항목 | 바닐라 Claude Code | oh-my-claudecode |
|------|-------------------|-----------------|
| **에이전트** | 단일 AI 인스턴스 | 32개 전문 에이전트 자동 위임 |
| **인터페이스** | 명령어 학습 필요 | 자연어 인터페이스 |
| **비용** | 단일 모델 사용 | 작업별 최적 모델 선택, 30-50% 절감 |
| **속도** | 순차적 처리 | 병렬 처리로 3-5배 향상 (Ultrapilot) |
| **지속성** | 작업 조기 중단 가능 | Ralph 모드로 검증까지 자동 재시도 |
| **컨텍스트** | 수동 관리 | Notepad Wisdom + 스킬 자동 추출 |
| **품질 보증** | 수동 테스팅 | BUILD/TEST/LINT 자동 검증 |
| **모니터링** | 제한적 | 실시간 HUD + 애널리틱스 대시보드 |

---

## 9. 이전 테스트 결과 요약 (Formula Checker PRD)

### 테스트 환경
- **PRD**: Formula Checker (WAI 모듈 기반 계산 스크립트 검증 도구)
- **테스트 날짜**: 2026-01-23
- **테스트 구성**: with-omc / without-omc 비교

### with-omc 결과
- **Test A (구현)**: PRD 100% 충족, 14개 파일 생성, ~2,000 lines
- **Test B (피드백 반영)**: JSON 내보내기 기능 정상 추가
- **Test C (수정 방식)**: 부분 수정 방식으로 기존 코드 영향 최소화
- **Test D (스킬 관찰)**: 명시적 스킬 호출 없이 hooks만으로 작업 완료

### 주요 관찰
1. oh-my-claudecode hooks가 매 응답마다 자동 실행됨
2. 기본 구현 작업에서는 명시적 스킬 호출 없이도 완료 가능
3. 플러그인 효과는 **복잡한 작업/계획 수립 시 더 두드러질 것**으로 예상

---

## 10. 다음 테스트 계획

### 새로운 PRD: ReadAlongBuddy
- **제품**: 어린이 책 읽기 웹 애플리케이션
- **기술 스택**: Python/Streamlit
- **핵심 기능**: 이미지 OCR → 텍스트 추출 → TTS 음성 재생
- **위치**: `docs/buddy_PRD.md`

### 테스트 관점
이전 Formula Checker 테스트에서 발견된 "복잡한 작업에서 효과가 더 클 것"이라는 가설 검증:
- 웹 프론트엔드 (Streamlit UI) → `designer` 에이전트 활용 여부
- 외부 API 연동 (OCR, TTS) → `researcher` 에이전트 활용 여부
- 멀티 Phase 기능 구현 → `planner`, `ralph` 모드 효과
- 매직 키워드/명시적 스킬 호출 시 차이

---

*이 문서는 플러그인 테스트 참고용으로 작성되었습니다.*
