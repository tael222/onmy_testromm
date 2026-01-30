# Test Metrics - ReadAlongBuddy (with-omc)

## Test Info
- **Test ID**: test-buddy-20260128
- **Date**: 2026-01-28
- **Plugin**: with-omc (oh-my-claudecode v3.7.2)
- **PRD**: ReadAlongBuddy (docs/buddy_PRD.md)
- **Target**: Phase 1(MVP) + Phase 2 + Phase 3 전체 (FR-001 ~ FR-016)
- **사용 스킬**: ralph-init → ralph (ultrawork 자동 활성화) x2회

## Token Usage

### Phase 1 (MVP) 완료 시점
- 세션 내 누적 (Phase 1 + 환경설정 + 분석 리포트 포함)
- 정확한 수치는 세션 종료 시 /cost 명령으로 확인 필요
- **참고**: 이 세션에서는 OMC 가이드 문서 작성, Phase 1 구현, 분석 리포트 작성, 앱 실행 테스트까지 모두 포함

### Phase 2+3 추가 구현
- Phase 1 완료 직후 연속 세션으로 진행
- ralph-init + ralph 2차 실행으로 13개 User Story 구현
- 5개 에이전트 동시 병렬 실행 (ultrawork)
- 정확한 수치는 세션 종료 시 /cost 명령으로 확인 필요

## Agent Usage Summary (전체 세션)

| 에이전트 | 모델 티어 | 호출 횟수 | 용도 |
|---------|----------|----------|------|
| MAIN (Opus 4.5) | MAIN | 전체 세션 | 오케스트레이터, 판단, 검증 |
| executor (Sonnet) | MEDIUM | 5회 | 코드 구현 (P1 초기+수정, P2+3 모듈A/B/C + 수정) |
| executor-high (Opus) | HIGH | 1회 | app.py 전체 재작성 (709줄) |
| executor-low (Haiku) | LOW | 1회 | requirements.txt + packages.txt 업데이트 |
| writer (Haiku) | LOW | 1회 | README.md 작성 |
| architect (Opus) | HIGH | 2회 | Phase 1 검증(2건 이슈) + Phase 2+3 검증(11건 이슈) |

## Skill Usage Summary

| 스킬 | 호출 방식 | 횟수 | 용도 |
|------|----------|------|------|
| ralph-init | 슬래시커맨드 | 2회 | Phase 1 PRD(7 US) + Phase 2+3 PRD(13 US) 분해 |
| ralph | 슬래시커맨드 | 2회 | Phase 1 자율 루프 + Phase 2+3 자율 루프 |

## Implementation Summary

| 항목 | Phase 1 | Phase 2+3 | 전체 |
|------|---------|-----------|------|
| User Stories | 7개 | 13개 | 20개 |
| 소스 파일 수 | 5개 | 5개 신규 + 4개 수정 | 10개 |
| 설정/문서 파일 | 4개 | 2개 수정 | 4개 |
| 총 소스 코드 라인 | ~277줄 | +~1,255줄 | ~1,532줄 |
| PRD 충족률 | 100% (FR-001~004) | 11/12 PASS + 2 PARTIAL | 전체: 14 PASS + 2 PARTIAL |
| Architect 검증 | PASS (2건→수정) | PASS (11건→4건 수정) | 2회 검증 완료 |
| Python 문법 검증 | ALL PASS | ALL PASS | 9개 파일 ALL PASS |
| 의존성 설치 | ALL SUCCESS | PyMuPDF 추가 | ALL SUCCESS |

## Ralph Loop Detail

### Phase 1 Ralph Loop
| 단계 | 설명 | 주체 에이전트 | 모델 | 결과 |
|------|------|-------------|------|------|
| 3a | US-001~007 병렬 구현 | executor(Sonnet) + writer(Haiku) | MEDIUM+LOW | 11파일 생성 |
| 3b | 문법 + 의존성 검증 | MAIN | MAIN | ALL PASS |
| 3c | Architect 리뷰 | architect(Opus) | HIGH | 2건 이슈 |
| 3d | 이슈 수정 | executor(Sonnet) | MEDIUM | 2파일 수정 |
| 3e | 문법 재검증 | MAIN | MAIN | ALL PASS |

### Phase 2+3 Ralph Loop
| 단계 | 설명 | 주체 에이전트 | 모델 | 결과 |
|------|------|-------------|------|------|
| 5a | 5개 에이전트 병렬 실행 | executor x3 + executor-low + executor-high | MED x3 + LOW + HIGH | 5신규 + 5수정 + 1재작성 |
| 5b | 문법 + 의존성 + import 검증 | MAIN | MAIN | ALL PASS |
| 5c | Architect 리뷰 | architect(Opus) | HIGH | 1 CRITICAL + 4 MED + 6 LOW |
| 5d | 이슈 수정 (4건) | executor(Sonnet) | MEDIUM | 2파일 수정 |
| 5e | 문법 재검증 | MAIN | MAIN | ALL PASS |

## Task Completion (전체)

### Phase 1 (MVP)
- [x] FR-001: 이미지 입력 (업로드 + 카메라 + 미리보기 + 재선택)
- [x] FR-002: 텍스트 인식 (pytesseract + 전처리 + 스피너 + 빈 텍스트 처리)
- [x] FR-003: 음성 합성 (gTTS + playbackRate 속도 조절 + 자동 재생)
- [x] FR-004: 텍스트 편집 (편집 + 복원 + 재읽기)

### Phase 2
- [x] FR-005: 따라 읽기 모드 (문장 분리 + 하이라이트 + 이전/다음)
- [~] FR-006: 발음 인식 STT (Web Speech API 렌더링, Streamlit 통신 제약으로 수동 입력 fallback)
- [x] FR-007: 발음 교정 피드백 (difflib 유사도 + 별점 + 단어별 하이라이트)
- [x] FR-008: 읽기 동기화 하이라이트 (문장 단위 하이라이트)
- [x] FR-009: 한글 지원 (OCR kor + TTS ko)
- [x] FR-010: 읽기 기록 (세션 내 저장 + 전체보기 + 듣기)
- [x] FR-011: 음성 선택 (5종: US/UK/AU/IN/한국어)

### Phase 3
- [x] FR-012: PDF 업로드 (PyMuPDF 페이지 추출 + 네비게이션)
- [x] FR-013: 책 생성 (이미지 + PDF → 책)
- [x] FR-014: 책 라이브러리 (3열 그리드 카드 + 읽기/삭제)
- [x] FR-015: 페이지 네비게이션 (이전/다음 + 페이지 카운터)
- [~] FR-016: 연속 읽기 (토글 활성화 + 수동 다음페이지)

### 비기능 요구사항
- [x] 아이 친화적 UI (큰 버튼, 밝은 색상, 한글 라벨, 3터치 이내)
- [x] 보안 (세션 내에서만 유지, 개인정보 미수집)
- [x] 저작권 보호 (공유 불가, 다운로드 불가, 세션 종료 시 삭제, 안내 문구)
- [x] 배포 준비 (Streamlit Cloud 호환, README)

## Observations

### Phase 1 관찰
1. ralph 스킬이 ultrawork를 자동 활성화하여 병렬 에이전트 실행 수행
2. 오케스트레이터(MAIN)는 직접 코드 작성하지 않고 executor/writer에게만 위임
3. Architect(Opus) 검증에서 gTTS 속도 한계 이슈를 발견하여 JS playbackRate로 해결
4. OCR 후 TTS 자동 실행 누락도 Architect가 발견하여 수정
5. ralph 루프: 구현 → 검증 → Architect → 수정 → 재검증 (총 5단계)
6. 에이전트 모델 라우팅: 코드 구현은 Sonnet, 문서는 Haiku, 검증은 Opus (비용 최적화)

### Phase 2+3 관찰
7. Phase 2+3는 5개 에이전트 동시 병렬 실행 (Phase 1의 2개 대비 2.5배)
8. app.py 재작성은 executor-high(Opus)에게 위임 (709줄, 가장 복잡한 작업)
9. 모듈 인터페이스를 사전 설계하여 병렬 에이전트 간 의존성 최소화
10. Architect(Opus) Phase 2+3 검증에서 11건 이슈 발견 (Phase 1의 2건 대비 5.5배)
11. STT의 Streamlit 프레임워크 제약은 근본적 한계 (서버 렌더링 vs 브라우저 이벤트)
12. 연속 읽기도 동일한 Streamlit 제약 (오디오 종료 이벤트 감지 불가)
13. Phase 1 코드 위에 확장 시 기존 기능 보존 성공 (Phase 1 ALL INTACT)
14. 코드량 5.5배 증가 (277줄 → 1,532줄), 에이전트 사용량은 약 3배 증가

### Bug Fix 관찰 (Phase 1+2+3 완료 후)
15. 사용자 수동 테스트에서 흐린 이미지 OCR 품질 이슈 발견
16. 버그 수정 작업은 MAIN이 직접 수행 (에이전트 위임 불필요한 단순 작업)
17. OpenCV 고급 전처리 추가로 OCR 정확도 대폭 개선 (인식불가 → 읽기 가능)
18. 스마트 선택 알고리즘: 기본/고급 전처리 중 더 좋은 결과 자동 선택

## Bug Fixes Summary

| 단계 | 이슈 | 수정 내용 | 결과 |
|------|------|----------|------|
| STEP-007 | 흐린 이미지 OCR 품질 저하 | OpenCV 고급 전처리 + 스마트 선택 | 인식불가 → 읽기 가능 |

### OCR 개선 상세

**수정 파일**: `modules/ocr.py` (21줄 → 110줄)

**추가 기능**:
1. `preprocess_image_basic()`: PIL 전용 기본 전처리 (업스케일, 대비, 샤프닝)
2. `preprocess_image_advanced()`: OpenCV 고급 전처리 (노이즈 제거, 적응형 이진화)
3. `_count_valid_words()`: OCR 결과 품질 추정
4. 스마트 선택: 두 방식 중 더 좋은 결과 자동 선택
5. Tesseract PSM 6: 책 페이지 텍스트 블록 최적화

**테스트 결과**:
```
이전: "my ak Th nr helt pap pl pe hee teint ake da dh..."
이후: "They didn't think they could hear it if anyone found out about the Potters..."
```
