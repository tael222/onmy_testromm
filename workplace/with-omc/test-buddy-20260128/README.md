# ReadAlongBuddy

**아이들을 위한 책 페이지 사진 인식 및 음성 읽기 Streamlit 웹 애플리케이션**

## 프로젝트 소개

ReadAlongBuddy는 아이들이 책의 페이지를 사진으로 찍으면 AI가 텍스트를 인식하고 음성으로 읽어주는 교육용 웹 애플리케이션입니다. 이 앱을 통해 아이들은 독립적인 학습 경험을 하면서 영어 발음과 독서 능력을 향상시킬 수 있습니다.

## 주요 기능

- **📸 이미지 업로드 및 카메라 캡처**: 사용자가 책 페이지 사진을 업로드하거나 웹캠으로 직접 촬영 가능
- **🔍 OCR 텍스트 추출**: Tesseract OCR을 사용한 고정밀 텍스트 인식
- **🔊 TTS 음성 읽기**: Google Text-to-Speech로 자연스러운 음성 출력
- **✏️ 텍스트 편집**: 인식된 텍스트를 사용자가 직접 수정 및 편집 가능
- **👶 어린이 친화적 UI**: 직관적이고 컬러풀한 사용자 인터페이스

## 기술 스택

- **Python 3.12+**
- **Streamlit**: 웹 애플리케이션 프레임워크
- **pytesseract**: Tesseract OCR Python 바인딩
- **gTTS**: Google Text-to-Speech 라이브러리
- **Pillow**: 이미지 처리 라이브러리

## 필수 요구사항

- Python 3.12 이상
- Tesseract OCR (시스템에 설치되어야 함)

## 설치 방법

### 1단계: 프로젝트 클론 및 디렉토리 이동

```bash
git clone <repository-url>
cd workplace/with-omc/test-buddy-20260128
```

### 2단계: Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 3단계: Tesseract OCR 설치

Tesseract OCR을 시스템에 설치해야 합니다.

**Windows:**
- [Tesseract OCR GitHub Releases](https://github.com/tesseract-ocr/tesseract)에서 설치 파일 다운로드
- 설치 마법사를 따라 기본 경로(`C:\Program Files\Tesseract-OCR`)에 설치

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

자세한 설치 방법은 [Tesseract OCR GitHub Repository](https://github.com/tesseract-ocr/tesseract)를 참조하세요.

## 실행 방법

```bash
streamlit run app.py
```

웹 브라우저가 자동으로 열리며, 로컬 주소 `http://localhost:8501`에서 애플리케이션을 사용할 수 있습니다.

## 프로젝트 구조

```
test-buddy-20260128/
├── README.md                 # 프로젝트 설명서
├── app.py                    # 메인 Streamlit 애플리케이션
├── requirements.txt          # Python 패키지 의존성
├── packages.txt              # Streamlit Cloud 시스템 패키지
├── modules/
│   ├── __init__.py
│   ├── ocr.py               # OCR 텍스트 추출 모듈
│   ├── tts.py               # TTS 음성 생성 모듈
│   └── ui.py                # 사용자 인터페이스 구성 모듈
└── assets/
    └── [이미지 및 리소스 파일]
```

### 모듈 설명

- **app.py**: Streamlit의 메인 진입점으로, 전체 애플리케이션 흐름 관리
- **modules/ocr.py**: Tesseract OCR을 사용한 이미지 텍스트 추출 기능 제공
- **modules/tts.py**: gTTS를 사용한 텍스트 음성 변환 기능 제공
- **modules/ui.py**: Streamlit UI 컴포넌트 구성 및 사용자 인터페이스 관리

## 배포 방법

### Streamlit Cloud 배포

1. GitHub 저장소에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에 계정 생성
3. 새 앱 생성 시 GitHub 저장소 연결
4. 배포 설정 완료

**주의**: `packages.txt` 파일에 Tesseract OCR이 포함되어 있어야 합니다.

packages.txt 예시:
```
tesseract-ocr
```

## 개인정보 보호 및 보안

- **이미지 저장 안 함**: 업로드된 모든 이미지는 세션 종료 후 자동으로 삭제됩니다.
- **개인정보 미수집**: 사용자의 어떤 개인정보도 수집하지 않습니다.
- **세션 기반**: 모든 데이터는 사용자의 세션 내에서만 유지되며, 다른 사용자와 공유되지 않습니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 기여 가이드

버그 리포트 및 기능 제안은 GitHub Issues를 통해 제출해 주세요.

## 문의 및 지원

문제가 발생하거나 추가 도움이 필요하신 경우, GitHub 저장소의 Issues 섹션을 통해 연락해 주세요.
