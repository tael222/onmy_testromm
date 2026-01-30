"""UI module for ReadAlongBuddy - child-friendly interface components."""

import streamlit as st

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&family=Nunito:wght@600;700;800&display=swap');

    :root {
        --primary-pastel: #FFB4D5;
        --secondary-pastel: #B4E4FF;
        --accent-pastel: #FFFFD6;
        --success-pastel: #B6FFA1;
        --warning-pastel: #FFE5B4;
        --peach-pastel: #FFD5C2;
        --lavender-pastel: #E5D4FF;
        --mint-pastel: #C2F5E9;
        --bg-gradient: linear-gradient(135deg, #FFF5E4 0%, #FFE5EC 25%, #E5F3FF 50%, #FFF5E4 100%);
        --card-shadow: 0 8px 32px rgba(255, 180, 213, 0.2);
        --card-shadow-hover: 0 12px 48px rgba(255, 180, 213, 0.35);
        --text-primary: #5D4E37;
        --text-secondary: #8B7355;
        --text-light: #A89F91;
    }

    /* Global styles */
    body, .stApp {
        background: var(--bg-gradient) !important;
        background-attachment: fixed !important;
        font-family: 'Noto Sans KR', 'Nunito', sans-serif !important;
    }

    /* Main container styling */
    .block-container {
        padding: 2rem 1rem !important;
        max-width: 1200px !important;
    }

    /* Headers with playful styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 50%, #FFD93D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        font-family: 'Nunito', 'Noto Sans KR', sans-serif;
        text-shadow: 2px 2px 4px rgba(255, 107, 157, 0.1);
        animation: titleFloat 3s ease-in-out infinite;
    }

    @keyframes titleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }

    .sub-title {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.4rem;
        margin-bottom: 2.5rem;
        font-weight: 600;
        animation: fadeIn 1s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Large child-friendly buttons */
    .stButton > button {
        min-height: 56px !important;
        font-size: 1.3rem !important;
        border-radius: 28px !important;
        padding: 14px 32px !important;
        background: linear-gradient(135deg, var(--primary-pastel) 0%, #FF95BA 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba(255, 180, 213, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        font-family: 'Nunito', 'Noto Sans KR', sans-serif !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(255, 180, 213, 0.6) !important;
        background: linear-gradient(135deg, #FF95BA 0%, var(--primary-pastel) 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(-2px) scale(0.98) !important;
    }

    /* Special read button */
    .read-btn > button {
        background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 100%) !important;
        font-size: 1.6rem !important;
        padding: 18px 40px !important;
        min-height: 64px !important;
        box-shadow: 0 8px 25px rgba(255, 107, 157, 0.5) !important;
    }

    .read-btn > button:hover {
        box-shadow: 0 12px 35px rgba(255, 107, 157, 0.7) !important;
    }

    /* Card-style info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 245, 250, 0.95) 100%);
        padding: 1.5rem;
        border-radius: 24px;
        border: 3px solid var(--mint-pastel);
        margin: 1.5rem 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
    }

    .info-box:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow-hover);
    }

    /* Step indicators with fun colors */
    .step-indicator {
        background: linear-gradient(135deg, #FFD93D 0%, #FFE66D 100%);
        color: var(--text-primary);
        padding: 0.75rem 1.5rem;
        border-radius: 30px;
        display: inline-block;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(255, 217, 61, 0.3);
        font-family: 'Nunito', 'Noto Sans KR', sans-serif;
        animation: bounceIn 0.6s ease;
    }

    @keyframes bounceIn {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Enhanced book cards */
    .book-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 250, 245, 0.98) 100%);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        border: 3px solid rgba(255, 180, 213, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .book-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, var(--primary-pastel) 0%, var(--secondary-pastel) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: 0;
    }

    .book-card:hover::before {
        opacity: 0.1;
    }

    .book-card:hover {
        border-color: var(--primary-pastel);
        transform: translateY(-6px) scale(1.02);
        box-shadow: var(--card-shadow-hover);
    }

    .book-card img {
        border-radius: 16px;
        max-height: 180px;
        object-fit: cover;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }

    .book-card .title {
        font-weight: 700;
        color: var(--text-primary);
        margin-top: 1rem;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
        font-family: 'Nunito', 'Noto Sans KR', sans-serif;
    }

    .book-card .meta {
        color: var(--text-light);
        font-size: 0.9rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }

    /* Page navigation */
    .page-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }

    .page-counter {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--secondary-pastel) 0%, #95D1FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Nunito', 'Noto Sans KR', sans-serif;
    }

    /* History items with soft styling */
    .history-item {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 250, 0.9) 100%);
        border-radius: 20px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 6px solid var(--primary-pastel);
        box-shadow: 0 4px 12px rgba(255, 180, 213, 0.15);
        transition: all 0.3s ease;
    }

    .history-item:hover {
        transform: translateX(4px);
        box-shadow: 0 6px 18px rgba(255, 180, 213, 0.25);
    }

    /* Copyright notices */
    .copyright-notice {
        text-align: center;
        color: var(--text-light);
        font-size: 0.85rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 2px solid rgba(255, 180, 213, 0.2);
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
    }

    .copyright-extended {
        text-align: center;
        color: #E74C3C;
        font-size: 0.9rem;
        margin: 1rem 0;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #FFF5F5 0%, #FFF0F0 100%);
        border-radius: 20px;
        border: 2px solid #FED7D7;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.1);
    }

    /* File uploader styling */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 24px !important;
        padding: 1.5rem !important;
        border: 3px dashed var(--secondary-pastel) !important;
        box-shadow: var(--card-shadow) !important;
    }

    div[data-testid="stFileUploader"] label {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        font-family: 'Nunito', 'Noto Sans KR', sans-serif !important;
    }

    /* Expanders and containers */
    .stExpander, .element-container > div {
        background: rgba(255, 255, 255, 0.85) !important;
        border-radius: 24px !important;
        padding: 1.5rem !important;
        box-shadow: var(--card-shadow) !important;
        border: 2px solid rgba(255, 180, 213, 0.15) !important;
    }

    /* Mode selector */
    .mode-selector {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        justify-content: center;
        flex-wrap: wrap;
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 16px !important;
        border: 2px solid var(--secondary-pastel) !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        background: rgba(255, 255, 255, 0.9) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary-pastel) !important;
        box-shadow: 0 0 0 3px rgba(255, 180, 213, 0.2) !important;
    }

    /* Animations for page load */
    .element-container {
        animation: slideUp 0.5s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
