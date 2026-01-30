---
name: code-review-evaluator
description: "PRD 기반 코드 완성도 평가 스킬. 사용 시점: (1) '코드 리뷰해줘', '코드 평가해줘' 요청 시, (2) PRD 대비 구현 완성도 확인 시, (3) '코드 분석', '코드 품질 체크' 요청 시. Python과 C# Unity 코드를 우선 지원하며, 문법/로직/구조/효율성/명명규칙을 평가하여 100점 만점 종합점수와 항목별 A/B/C/D 등급을 제공. MD 리포트와 1장 PPTX 요약 생성."
---

# Code Review Evaluator

PRD(Product Requirements Document) 기반으로 코드 완성도를 평가하고 리포트를 생성하는 스킬.

## 평가 워크플로우

### 1단계: 입력 수집

필수 입력:
- **PRD 문서** (MD 파일): 요구사항 명세
- **코드 파일/폴더**: 평가 대상 소스코드

### 2단계: 평가 수행

[references/evaluation-criteria.md](references/evaluation-criteria.md)의 기준에 따라 7개 항목 평가:

| 항목 | 가중치 | 설명 |
|------|--------|------|
| 로직 정확성 | 25% | PRD 요구사항의 정확한 구현 |
| 완결성 | 25% | PRD 대비 기능 구현 완료율 |
| 구조적 연결성 | 15% | 클래스/함수/변수 간 연결 |
| 문법적 정확성 | 10% | 컴파일/실행 오류 없음 |
| 효율성 | 10% | 알고리즘/자원 사용 최적화 |
| 명명 규칙 | 10% | 네이밍 컨벤션 준수 |
| 일관성 | 5% | 코드 스타일 통일성 |

### 3단계: 점수 산출

**등급 기준:**
- A: 90-100점 (우수)
- B: 75-89점 (양호)
- C: 60-74점 (보통)
- D: 60점 미만 (개선 필요)

**종합 점수:** 각 항목 점수 × 가중치의 합 (100점 만점)

### 4단계: 리포트 생성

1. **MD 리포트** 작성 (상세 평가 결과)
2. **PPTX 요약** 생성 (`scripts/generate_report.js` 사용)

## 출력물 형식

### MD 리포트 구조

```markdown
# 코드 완성도 평가 리포트

## 평가 개요
- 프로젝트명: [프로젝트명]
- 평가일: [날짜]
- 대상 언어: [Python/C#]

## 종합 점수: [점수]/100

## 항목별 평가

### 로직 정확성 (25%) - 등급: [A/B/C/D]
[상세 평가 내용]

### 완결성 (25%) - 등급: [A/B/C/D]
[PRD 대비 구현 현황]

... (각 항목별 반복)

## 주요 발견사항
- 강점: [리스트]
- 개선점: [리스트]

## 권장사항
[개선 권장 내용]
```

### PPTX 생성

```bash
node scripts/generate_report.js \
  --title "프로젝트명" \
  --score 85 \
  --grades '{"logic":"A","completeness":"B","structure":"A","syntax":"A","efficiency":"B","naming":"B","consistency":"A"}' \
  --summary "핵심 평가 요약 (2-3문장)" \
  --output report.pptx
```

## 언어별 평가 가이드

### Python
- PEP 8 스타일 가이드 준수 확인
- Type hints 사용 여부
- docstring 작성 여부

### C# Unity
- Unity 코딩 컨벤션 준수
- MonoBehaviour 생명주기 올바른 사용
- SerializeField, public/private 적절한 사용

## 평가 시 주의사항

1. PRD에 명시되지 않은 기능은 평가에서 제외
2. 주관적 판단보다 객관적 기준 우선
3. 언어별 관용적 표현 존중
4. 성능 평가는 명백한 비효율만 지적
