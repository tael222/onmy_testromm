"""UI module for ReadAlongBuddy - child-friendly interface components."""

import streamlit as st

CUSTOM_CSS = """
<style>
    .main-title {
        text-align: center;
        color: #FF6B6B;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #4ECDC4;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        font-size: 1.3rem;
        padding: 0.8rem 2rem;
        border-radius: 20px;
        font-weight: bold;
        width: 100%;
    }
    .read-btn > button {
        background-color: #FF6B6B;
        color: white;
        font-size: 1.5rem;
        padding: 1rem 2rem;
    }
    .info-box {
        background-color: #E8F8F5;
        padding: 1rem;
        border-radius: 15px;
        border: 2px solid #4ECDC4;
        margin: 1rem 0;
    }
    .copyright-notice {
        text-align: center;
        color: #95A5A6;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding: 0.5rem;
        border-top: 1px solid #E0E0E0;
    }
    div[data-testid="stFileUploader"] label {
        font-size: 1.2rem;
    }
    .step-indicator {
        background-color: #FFE66D;
        color: #2C3E50;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    /* Phase 2+3 additions */
    .mode-selector {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .book-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid #E0E0E0;
        transition: all 0.3s;
        cursor: pointer;
        text-align: center;
    }
    .book-card:hover {
        border-color: #4ECDC4;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(78,205,196,0.3);
    }
    .book-card img {
        border-radius: 8px;
        max-height: 150px;
        object-fit: cover;
    }
    .book-card .title {
        font-weight: bold;
        color: #2C3E50;
        margin-top: 0.5rem;
        font-size: 1rem;
    }
    .book-card .meta {
        color: #95A5A6;
        font-size: 0.8rem;
    }
    .page-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
    }
    .page-counter {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4ECDC4;
    }
    .history-item {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
    }
    .copyright-extended {
        text-align: center;
        color: #E74C3C;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #FFF5F5;
        border-radius: 8px;
        border: 1px solid #FECACA;
    }
</style>
"""


def inject_custom_css():
    """Inject custom CSS for child-friendly styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def show_header():
    """Display the app header with title and subtitle."""
    st.markdown('<h1 class="main-title">ReadAlongBuddy</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">마법의 책 읽기 친구</p>', unsafe_allow_html=True)


def show_step(number: int, label: str):
    """Display a step indicator."""
    st.markdown(
        f'<span class="step-indicator">Step {number}: {label}</span>',
        unsafe_allow_html=True,
    )


def show_copyright():
    """Display copyright notice."""
    st.markdown(
        '<div class="copyright-notice">'
        "이 앱은 개인 학습 용도로만 사용해 주세요. "
        "책의 저작권은 원저작자에게 있습니다. "
        "촬영된 이미지는 저장되지 않으며, 세션 종료 시 자동 삭제됩니다."
        "</div>",
        unsafe_allow_html=True,
    )


def show_copyright_extended():
    """Display extended copyright notice for book library features."""
    st.markdown(
        '<div class="copyright-extended">'
        "⚠️ 저작권 안내: 생성된 책은 개인 학습 용도로만 사용 가능합니다. "
        "외부 공유, 다운로드, 내보내기가 제한됩니다. "
        "세션 종료 시 모든 데이터가 자동 삭제됩니다."
        "</div>",
        unsafe_allow_html=True,
    )


def show_page_nav_html(current: int, total: int) -> str:
    """Generate page navigation HTML."""
    return (
        f'<div class="page-nav">'
        f'<span class="page-counter">{current} / {total} 페이지</span>'
        f'</div>'
    )
