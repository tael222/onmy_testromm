# Environment Analysis

## Claude Code
- **Version**: 2.1.15

## Installed Plugin
| Plugin | Version | Scope |
|--------|---------|-------|
| oh-my-claudecode | 3.3.6 | user |

---

## oh-my-claudecode 기능 분석

### Skills (32개)

| Skill | 설명 | 분류 |
|-------|------|------|
| `/analyze` | 심층 분석 및 조사 | 분석 |
| `/autopilot` | 아이디어에서 코드까지 완전 자율 실행 | 자동화 |
| `/cancel-autopilot` | autopilot 취소 | 제어 |
| `/cancel-ralph` | ralph 취소 | 제어 |
| `/cancel-ultraqa` | ultraqa 취소 | 제어 |
| `/cancel-ultrawork` | ultrawork 취소 | 제어 |
| `/deepinit` | 계층적 AGENTS.md로 코드베이스 초기화 | 설정 |
| `/deepsearch` | 철저한 코드베이스 검색 | 탐색 |
| `/doctor` | oh-my-claudecode 설치 문제 진단 | 유틸 |
| `/frontend-ui-ux` | 디자인 목업 없이도 UI/UX 구현 | 개발 |
| `/git-master` | Git 전문가 (atomic commits, rebasing) | 개발 |
| `/help` | 플러그인 사용 가이드 | 유틸 |
| `/hud` | HUD 표시 옵션 설정 | 설정 |
| `/learner` | 현재 대화에서 학습된 skill 추출 | 학습 |
| `/note` | notepad.md에 메모 저장 | 유틸 |
| `/omc-default` | 로컬 프로젝트에 OMC 설정 | 설정 |
| `/omc-default-global` | 전역 OMC 설정 | 설정 |
| `/omc-setup` | oh-my-claudecode 초기 설정 | 설정 |
| `/orchestrate` | 멀티 에이전트 오케스트레이션 모드 | 자동화 |
| `/plan` | Planner와 계획 세션 시작 | 계획 |
| `/planner` | 인터뷰 워크플로우로 전략적 계획 | 계획 |
| `/ralph` | 완료까지 자기참조 루프 + architect 검증 | 자동화 |
| `/ralph-init` | PRD 초기화 | 계획 |
| `/ralplan` | Planner, Architect, Critic 합의까지 반복 | 계획 |
| `/release` | oh-my-claudecode 릴리즈 워크플로우 | 유틸 |
| `/research` | 병렬 scientist 에이전트로 종합 연구 | 연구 |
| `/review` | Critic으로 계획 검토 | 품질 |
| `/tdd` | 테스트 주도 개발 워크플로우 | 품질 |
| `/ultraqa` | QA 사이클 (테스트→검증→수정→반복) | 품질 |
| `/ultrawork` | 병렬 에이전트로 최대 성능 모드 | 자동화 |

### Magic Keywords (자동 활성화)

| 키워드 | 효과 |
|--------|------|
| `ralph` | 완료까지 지속 모드 |
| `ralplan` | 합의까지 반복 계획 |
| `ulw` | 최대 병렬 실행 |
| `plan` | 계획 인터뷰 시작 |
| `autopilot` / `ap` | 완전 자율 실행 |

### Agents (32개)

| Agent | Model | 용도 |
|-------|-------|------|
| analyst | Opus | 사전 계획 요구사항 분석 |
| architect | Opus | 전략적 아키텍처 & 디버깅 |
| architect-medium | Sonnet | 중간 복잡도 아키텍처 |
| architect-low | Haiku | 간단한 코드 질문 |
| build-fixer | Sonnet | 빌드/타입 오류 해결 |
| build-fixer-low | Haiku | 간단한 빌드 오류 |
| code-reviewer | Sonnet | 코드 품질 검토 |
| code-reviewer-low | Haiku | 빠른 코드 검토 |
| critic | Opus | 작업 계획 검토/비평 |
| designer | Sonnet | UI/UX 디자이너-개발자 |
| designer-high | Opus | 복잡한 UI 아키텍처 |
| designer-low | Haiku | 간단한 스타일링 |
| executor | Sonnet | 구현 작업 실행 |
| executor-high | Opus | 복잡한 다중 파일 작업 |
| executor-low | Haiku | 간단한 단일 파일 작업 |
| explore | Haiku | 빠른 코드베이스 검색 |
| explore-medium | Sonnet | 추론이 포함된 검색 |
| planner | Opus | 인터뷰 워크플로우 전략 계획 |
| qa-tester | Sonnet | tmux를 사용한 CLI 테스트 |
| researcher | Sonnet | 외부 문서 및 참조 연구 |
| researcher-low | Haiku | 빠른 문서 조회 |
| scientist | Sonnet | 데이터 분석 및 연구 실행 |
| scientist-high | Opus | 복잡한 연구, 가설 검증, ML |
| scientist-low | Haiku | 빠른 데이터 검사 |
| security-reviewer | Sonnet | 보안 취약점 탐지 |
| security-reviewer-low | Haiku | 빠른 보안 스캔 |
| tdd-guide | Sonnet | TDD 방법론 강제 |
| tdd-guide-low | Haiku | 빠른 테스트 제안 |
| vision | Sonnet | 이미지, PDF, 다이어그램 분석 |
| writer | Haiku | README, API 문서, 주석 작성 |

### Hooks (자동 실행)

| Hook | 트리거 | 기능 |
|------|--------|------|
| keyword-detector | UserPromptSubmit | 메시지에서 키워드 감지 |
| skill-injector | UserPromptSubmit | skill 자동 주입 |
| session-start | SessionStart | 세션 시작 시 초기화 |
| pre-tool-enforcer | PreToolUse | 도구 사용 전 검증 |
| post-tool-verifier | PostToolUse | 도구 사용 후 검증 |
| persistent-mode | Stop | 지속 모드 처리 |

---

## 잠재적 방해 요소 분석

### 고려 사항
1. **Hook 오버헤드**: 모든 프롬프트/도구 사용에 hook 실행 → 토큰 측정에 영향 가능
2. **자동 활성화**: 특정 키워드로 의도치 않은 모드 활성화 가능
3. **system-reminder**: hook에서 주입하는 메시지가 컨텍스트 사용

### 테스트 시 주의점
- `without-omc` 테스트 시 플러그인 완전 비활성화 필요
- 키워드 사용 시 의도치 않은 모드 활성화 주의
- 토큰 측정 시 hook 오버헤드 고려

---

## 플러그인 비활성화 방법

```bash
# settings.json에서 비활성화
# ~/.claude/settings.json
{
  "enabledPlugins": {
    "oh-my-claudecode@omc": false
  }
}
```

또는 새 세션에서 플러그인 없이 시작

---

## 결론

현재 환경에는 **oh-my-claudecode 3.3.6** 단일 플러그인만 설치되어 있어 테스트 환경이 깔끔합니다. 불필요한 플러그인은 없습니다.

테스트 진행 시:
1. **with-omc**: 현재 설정 그대로 사용
2. **without-omc**: settings.json에서 `false`로 변경 후 새 세션 시작
