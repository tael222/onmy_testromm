"""ReadAlongBuddy - Phase 1+2+3+4 Complete Application.

Main Streamlit entrypoint integrating:
  Phase 1: Image OCR, TTS playback, text editing
  Phase 2: Language/voice selection, read-along mode, STT, pronunciation feedback, history
  Phase 3: PDF upload, book library, page navigation, continuous reading, copyright
  Phase 4: Buddy character, rewards (stars/badges/levels), stats dashboard, sound effects
"""

import streamlit as st
from PIL import Image

from modules.ocr import LANG_MAP, extract_text
from modules.tts import (
    DEFAULT_VOICE,
    get_voice_list,
    synthesize_speech,
    synthesize_sentence,
    get_audio_html,
)
from modules.ui import (
    inject_custom_css,
    show_header,
    show_step,
    show_copyright,
    show_copyright_extended,
    show_page_nav_html,
)
from modules.reading_mode import split_sentences, get_highlighted_text_html
from modules.stt import render_stt_ui
from modules.pronunciation import calculate_similarity, get_word_comparison, get_feedback_html
from modules.pdf_handler import is_pdf_supported, extract_pages_from_pdf
from modules.book_manager import (
    Book,
    get_book_card_html,
    init_library,
    add_book_to_library,
    remove_book_from_library,
    add_to_reading_history,
)
# Phase 4: Buddy, Rewards, Stats, Sound
from modules.buddy import BuddyMood, get_buddy_component, get_mood_for_accuracy
from modules.rewards import (
    init_reward_state,
    get_reward_state,
    award_stars,
    render_stars_html,
    render_level_badge_html,
    render_badge_popup_html,
    get_rewards_css,
)
from modules.stats import init_stats, record_reading, record_page, get_stats_component, get_stats_css
from modules.sound import (
    get_sound_init_html,
    play_star_sound,
    play_correct_sound,
    play_badge_sound,
    is_sound_enabled,
    toggle_sound,
    get_sound_toggle_html,
)

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ReadAlongBuddy",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ---------------------------------------------------------------------------
# Session State Initialisation
# ---------------------------------------------------------------------------
_DEFAULTS: dict = {
    # Phase 1
    "original_text": "",
    "recognized_text": "",
    "audio_bytes": None,
    # Phase 2
    "app_mode": "📖 읽기 모드",
    "ocr_lang": "eng",
    "voice": DEFAULT_VOICE,
    "sentences": [],
    "current_sentence_idx": 0,
    "stt_result": "",
    # Phase 3
    "current_book_index": None,
    "continuous_reading": False,
    "current_image": None,
    "pdf_pages": [],
    "pdf_page_idx": 0,
}

for key, default in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Initialise library / history lists via book_manager helper
init_library(st.session_state)

# Initialize Phase 4 systems: rewards and stats
init_reward_state()
init_stats()

# ---------------------------------------------------------------------------
# Sidebar  --  Navigation + Settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 메뉴")
    mode = st.radio(
        "모드 선택",
        ["📖 읽기 모드", "🎯 따라 읽기", "📚 내 책장", "📋 읽기 기록"],
        index=["📖 읽기 모드", "🎯 따라 읽기", "📚 내 책장", "📋 읽기 기록"].index(
            st.session_state.app_mode
        )
        if st.session_state.app_mode in ["📖 읽기 모드", "🎯 따라 읽기", "📚 내 책장", "📋 읽기 기록"]
        else 0,
        key="sidebar_mode",
    )
    st.session_state.app_mode = mode

    st.markdown("---")
    st.markdown("### 설정")

    # Language selection
    lang_label = st.selectbox(
        "인식 언어",
        list(LANG_MAP.keys()),
        index=list(LANG_MAP.values()).index(st.session_state.ocr_lang)
        if st.session_state.ocr_lang in LANG_MAP.values()
        else 0,
        key="sidebar_lang",
    )
    st.session_state.ocr_lang = LANG_MAP[lang_label]

    # Voice selection
    voice_choice = st.selectbox(
        "읽기 목소리",
        get_voice_list(),
        index=get_voice_list().index(st.session_state.voice)
        if st.session_state.voice in get_voice_list()
        else 0,
        key="sidebar_voice",
    )
    st.session_state.voice = voice_choice

    # Sound toggle (Phase 4)
    st.markdown("---")
    if st.button(get_sound_toggle_html(), key="sound_toggle"):
        toggle_sound()
        st.rerun()

    # Display total stars and level (Phase 4)
    st.markdown("---")
    st.markdown("### 내 현황")
    reward_state = get_reward_state()
    st.markdown(f"**{reward_state.current_level.emoji} {reward_state.current_level.korean_name}**")
    st.markdown(f"⭐ 모은 별: **{reward_state.total_stars}**개")

# ---------------------------------------------------------------------------
# Header (always shown)
# ---------------------------------------------------------------------------
show_header()


# ===================================================================
# Helper: determine TTS lang_override from ocr_lang
# ===================================================================
def _tts_lang_override() -> str | None:
    """Return gTTS lang code matching the current OCR language setting."""
    ocr = st.session_state.ocr_lang
    if ocr in ("kor", "eng+kor"):
        return "ko"
    # When English, let the voice setting drive gTTS lang (no override)
    return None


# ===================================================================
# Helper: image acquisition (shared by reading mode & read-along)
# ===================================================================
def _acquire_image() -> Image.Image | None:
    """Show upload/camera/PDF tabs and return the selected image."""
    tab_labels = ["📁 사진 올리기", "📷 카메라로 찍기"]
    if is_pdf_supported():
        tab_labels.append("📄 PDF 올리기")

    tabs = st.tabs(tab_labels)
    image: Image.Image | None = None

    with tabs[0]:
        uploaded = st.file_uploader(
            "책 페이지 사진을 올려주세요",
            type=["jpg", "jpeg", "png", "webp"],
            key="file_upload",
        )
        if uploaded is not None:
            image = Image.open(uploaded)

    with tabs[1]:
        camera = st.camera_input("카메라로 책 페이지를 찍어주세요", key="camera")
        if camera is not None:
            image = Image.open(camera)

    if is_pdf_supported() and len(tabs) > 2:
        with tabs[2]:
            pdf_file = st.file_uploader(
                "PDF 파일을 올려주세요",
                type=["pdf"],
                key="pdf_upload",
            )
            if pdf_file is not None:
                pdf_bytes = pdf_file.read()
                pdf_key = f"pdf_{len(pdf_bytes)}_{pdf_bytes[:20]}"
                if st.session_state.get("_pdf_key") != pdf_key:
                    with st.spinner("PDF 페이지를 읽는 중..."):
                        st.session_state.pdf_pages = extract_pages_from_pdf(pdf_bytes)
                        st.session_state.pdf_page_idx = 0
                        st.session_state._pdf_key = pdf_key

                if st.session_state.pdf_pages:
                    total = len(st.session_state.pdf_pages)
                    idx = st.session_state.pdf_page_idx
                    st.markdown(
                        show_page_nav_html(idx + 1, total), unsafe_allow_html=True
                    )
                    col_prev, col_next = st.columns(2)
                    with col_prev:
                        if st.button("◀ 이전 페이지", key="pdf_prev", disabled=(idx <= 0)):
                            st.session_state.pdf_page_idx = max(0, idx - 1)
                            st.rerun()
                    with col_next:
                        if st.button("다음 페이지 ▶", key="pdf_next", disabled=(idx >= total - 1)):
                            st.session_state.pdf_page_idx = min(total - 1, idx + 1)
                            st.rerun()
                    image = st.session_state.pdf_pages[st.session_state.pdf_page_idx]

    return image


# ===================================================================
# Helper: perform OCR + TTS on a given image (returns True if text found)
# ===================================================================
def _run_ocr_tts(image: Image.Image) -> bool:
    """Run OCR and TTS, updating session state. Returns True if text found."""
    with st.spinner("책에서 글자를 찾는 중..."):
        text = extract_text(image, lang=st.session_state.ocr_lang)

    if text:
        st.session_state.original_text = text
        st.session_state.recognized_text = text
        st.session_state.current_image = image
        st.success("글자를 찾았어요!")

        # Auto-save to reading history
        add_to_reading_history(st.session_state, text, image)

        with st.spinner("목소리를 만들고 있어요..."):
            audio = synthesize_speech(
                text,
                speed="보통",
                voice=st.session_state.voice,
                lang_override=_tts_lang_override(),
            )
            st.session_state.audio_bytes = audio
        return True
    else:
        st.warning("글자를 찾지 못했어요. 다른 페이지를 시도해 보세요!")
        return False


# ===================================================================
# Helper: reset reading state
# ===================================================================
def _reset_reading_state():
    st.session_state.original_text = ""
    st.session_state.recognized_text = ""
    st.session_state.audio_bytes = None
    st.session_state.sentences = []
    st.session_state.current_sentence_idx = 0
    st.session_state.stt_result = ""
    st.session_state.pdf_pages = []
    st.session_state.pdf_page_idx = 0
    st.session_state.current_image = None


# ###################################################################
#  MODE: 읽기 모드 (Reading Mode)
# ###################################################################
def render_reading_mode():
    """Phase 1 core flow + Phase 2/3 enhancements."""

    # -- Check if we are reading a book from the library --
    book: Book | None = None
    if st.session_state.current_book_index is not None:
        lib = st.session_state.book_library
        idx = st.session_state.current_book_index
        if 0 <= idx < len(lib):
            book = lib[idx]

    if book is not None:
        _render_book_reader(book)
        return

    # -- Normal single-image flow --
    show_step(1, "책 페이지를 보여주세요!")
    image = _acquire_image()

    if image is not None:
        st.image(image, caption="내가 고른 책 페이지", use_container_width=True)

        show_step(2, "글자를 찾고 있어요!")
        if st.button("📖 읽어줘!", key="read_btn", type="primary"):
            _run_ocr_tts(image)

    # -- Text editing + TTS --
    if st.session_state.recognized_text:
        show_step(3, "글자를 확인하고 들어봐요!")

        edited_text = st.text_area(
            "찾은 글자 (수정할 수 있어요)",
            value=st.session_state.recognized_text,
            height=200,
            key="text_editor",
        )

        col_restore, col_speed = st.columns([1, 1])
        with col_restore:
            if st.button("🔄 원래 글자로", key="restore_btn"):
                st.session_state.recognized_text = st.session_state.original_text
                st.rerun()
        with col_speed:
            speed = st.select_slider(
                "읽기 속도",
                options=["느리게", "보통", "빠르게"],
                value="보통",
                key="speed_slider",
            )

        if st.button("🔊 다시 읽어줘!", key="tts_btn", type="primary"):
            with st.spinner("목소리를 만들고 있어요..."):
                audio = synthesize_speech(
                    edited_text,
                    speed,
                    voice=st.session_state.voice,
                    lang_override=_tts_lang_override(),
                )
                st.session_state.audio_bytes = audio
                st.session_state.recognized_text = edited_text

        if st.session_state.audio_bytes:
            speed_val = st.session_state.get("speed_slider", "보통")
            audio_html = get_audio_html(
                st.session_state.audio_bytes, autoplay=True, speed=speed_val
            )
            st.markdown(audio_html, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("📸 새 페이지 읽기", key="new_page_btn"):
                _reset_reading_state()
                st.rerun()

    show_copyright()


# ###################################################################
#  Book reader (inside reading mode when a book is selected)
# ###################################################################
def _render_book_reader(book: Book):
    """Read through a book page by page with navigation."""
    show_copyright_extended()

    st.markdown(f"### 📖 {book.title}")

    page = book.get_current_page()
    if page is None:
        st.warning("이 책에 페이지가 없어요.")
        if st.button("📚 책장으로 돌아가기", key="back_empty"):
            st.session_state.current_book_index = None
            st.session_state.app_mode = "📚 내 책장"
            st.rerun()
        return

    # Page navigation
    total = book.page_count
    current_num = book.current_page + 1
    st.markdown(show_page_nav_html(current_num, total), unsafe_allow_html=True)

    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("◀ 이전", key="book_prev", disabled=(book.current_page <= 0)):
            book.prev_page()
            st.session_state.audio_bytes = None
            st.rerun()
    with col_n:
        if st.button("다음 ▶", key="book_next", disabled=(book.current_page >= total - 1)):
            book.next_page()
            st.session_state.audio_bytes = None
            st.rerun()

    # Continuous reading toggle
    st.session_state.continuous_reading = st.checkbox(
        "연속 읽기 (자동으로 다음 페이지)", value=st.session_state.continuous_reading, key="cont_read"
    )

    # Show page image
    st.image(page.image, caption=f"{current_num}페이지", use_container_width=True)

    # OCR if not done
    if not page.ocr_done:
        if st.button("📖 이 페이지 읽어줘!", key="book_read_btn", type="primary"):
            with st.spinner("글자를 찾는 중..."):
                text = extract_text(page.image, lang=st.session_state.ocr_lang)
            if text:
                page.text = text
                page.ocr_done = True
                add_to_reading_history(st.session_state, text, page.image)
                with st.spinner("목소리를 만들고 있어요..."):
                    audio = synthesize_speech(
                        text,
                        speed="보통",
                        voice=st.session_state.voice,
                        lang_override=_tts_lang_override(),
                    )
                    st.session_state.audio_bytes = audio
            else:
                st.warning("글자를 찾지 못했어요.")
    else:
        st.markdown(f"**텍스트:** {page.text}")
        if st.button("🔊 읽어줘!", key="book_tts_btn", type="primary"):
            with st.spinner("목소리를 만들고 있어요..."):
                audio = synthesize_speech(
                    page.text,
                    speed="보통",
                    voice=st.session_state.voice,
                    lang_override=_tts_lang_override(),
                )
                st.session_state.audio_bytes = audio

    if st.session_state.audio_bytes:
        html = get_audio_html(st.session_state.audio_bytes, autoplay=True, speed="보통")
        st.markdown(html, unsafe_allow_html=True)

        # Continuous reading: auto-advance with JS audio end detection
        if st.session_state.continuous_reading and book.current_page < total - 1:
            st.info("연속 읽기 모드: 오디오 재생이 끝나면 아래 버튼을 눌러 다음 페이지로 이동하세요.")
            if st.button("▶ 다음 페이지로", key="auto_next", type="primary"):
                book.next_page()
                st.session_state.audio_bytes = None
                st.rerun()

    st.markdown("---")
    if st.button("📚 책장으로 돌아가기", key="back_to_lib"):
        st.session_state.current_book_index = None
        st.session_state.audio_bytes = None
        st.session_state.app_mode = "📚 내 책장"
        st.rerun()

    show_copyright()


# ###################################################################
#  MODE: 따라 읽기 (Read-Along)
# ###################################################################
def render_readalong_mode():
    """Sentence-by-sentence read-along with STT + pronunciation feedback."""
    st.markdown("### 🎯 따라 읽기")
    st.info("문장을 하나씩 듣고, 따라 읽어보세요!")

    # -- If we don't have text yet, let user get text first --
    if not st.session_state.recognized_text:
        show_step(1, "먼저 책 페이지를 보여주세요!")
        image = _acquire_image()
        if image is not None:
            st.image(image, caption="내가 고른 책 페이지", use_container_width=True)
            if st.button("📖 읽어줘!", key="ra_read_btn", type="primary"):
                _run_ocr_tts(image)
                if st.session_state.recognized_text:
                    st.session_state.sentences = split_sentences(
                        st.session_state.recognized_text
                    )
                    st.session_state.current_sentence_idx = 0
                    st.rerun()
        show_copyright()
        return

    # -- Ensure sentences are split --
    if not st.session_state.sentences:
        st.session_state.sentences = split_sentences(st.session_state.recognized_text)
        st.session_state.current_sentence_idx = 0

    sentences = st.session_state.sentences
    idx = st.session_state.current_sentence_idx

    if not sentences:
        st.warning("문장을 나눌 수 없어요. 다른 페이지를 시도해 보세요!")
        if st.button("📸 새 페이지", key="ra_new"):
            _reset_reading_state()
            st.rerun()
        show_copyright()
        return

    total_s = len(sentences)
    idx = min(idx, total_s - 1)

    # -- Sentence progress --
    st.progress((idx + 1) / total_s)
    st.markdown(f"**문장 {idx + 1} / {total_s}**")

    # -- Highlighted text --
    highlighted_html = get_highlighted_text_html(sentences, idx)
    st.markdown(highlighted_html, unsafe_allow_html=True)

    # -- Play current sentence --
    current_sentence = sentences[idx]
    st.markdown(
        f'<div style="background:#E8F8F5; padding:1rem; border-radius:12px; '
        f'font-size:1.3rem; text-align:center; margin:0.5rem 0;">'
        f"<b>{current_sentence}</b></div>",
        unsafe_allow_html=True,
    )

    if st.button("🔊 이 문장 듣기", key="ra_play_sentence", type="primary"):
        with st.spinner("목소리를 만들고 있어요..."):
            audio = synthesize_sentence(
                current_sentence,
                speed="보통",
                voice=st.session_state.voice,
                lang_override=_tts_lang_override(),
            )
        html = get_audio_html(audio, autoplay=True, speed="보통", audio_id="ra-audio")
        st.markdown(html, unsafe_allow_html=True)

    # -- STT: user speaks --
    st.markdown("---")
    st.markdown("**🎤 이제 따라 읽어보세요!**")

    # Determine STT language
    stt_lang = "ko-KR" if st.session_state.ocr_lang in ("kor", "eng+kor") else "en-US"
    render_stt_ui(lang=stt_lang)

    # Fallback manual input (since JS postMessage cannot reliably reach Streamlit)
    st.markdown(
        '<p style="color:#888; font-size:0.9rem;">'
        "음성 인식이 안 되면 아래에 직접 입력하세요:</p>",
        unsafe_allow_html=True,
    )
    spoken_text = st.text_input(
        "내가 읽은 내용",
        value=st.session_state.stt_result,
        key="ra_stt_input",
        placeholder="여기에 읽은 내용을 입력하세요...",
    )

    # -- Pronunciation check with Phase 4 rewards --
    if st.button("✅ 발음 체크!", key="ra_check", type="primary"):
        if spoken_text.strip():
            st.session_state.stt_result = spoken_text.strip()
            score = calculate_similarity(current_sentence, spoken_text.strip())
            word_results = get_word_comparison(current_sentence, spoken_text.strip())
            feedback_html = get_feedback_html(score, word_results)
            st.markdown(feedback_html, unsafe_allow_html=True)

            # Phase 4: Award stars based on accuracy (convert ratio 0.0-1.0 to percentage 0-100)
            accuracy_percent = score * 100
            stars_earned, new_badges = award_stars(accuracy_percent)
            record_reading(current_sentence, accuracy_percent)

            # Display stars earned
            if stars_earned > 0:
                st.markdown(render_stars_html(stars_earned), unsafe_allow_html=True)
                st.markdown(play_star_sound(), unsafe_allow_html=True)

            # Display new badges earned
            for badge in new_badges:
                st.markdown(render_badge_popup_html(badge), unsafe_allow_html=True)
                st.markdown(play_badge_sound(), unsafe_allow_html=True)

            # Display buddy with mood based on accuracy
            buddy_mood = get_mood_for_accuracy(accuracy_percent)
            st.markdown(get_buddy_component(buddy_mood), unsafe_allow_html=True)

            # Play appropriate sound
            if accuracy_percent >= 70:
                st.markdown(play_correct_sound(), unsafe_allow_html=True)
        else:
            st.warning("먼저 문장을 읽어주세요!")

    # -- Navigation between sentences --
    st.markdown("---")
    col_sp, col_sn = st.columns(2)
    with col_sp:
        if st.button("◀ 이전 문장", key="ra_prev_s", disabled=(idx <= 0)):
            st.session_state.current_sentence_idx = idx - 1
            st.session_state.stt_result = ""
            st.rerun()
    with col_sn:
        if st.button("다음 문장 ▶", key="ra_next_s", disabled=(idx >= total_s - 1)):
            st.session_state.current_sentence_idx = idx + 1
            st.session_state.stt_result = ""
            st.rerun()

    if idx >= total_s - 1:
        st.balloons()
        st.success("모든 문장을 다 따라 읽었어요! 정말 잘했어요!")

    st.markdown("---")
    if st.button("📸 새 페이지로", key="ra_reset"):
        _reset_reading_state()
        st.rerun()

    show_copyright()


# ###################################################################
#  MODE: 내 책장 (Book Library)
# ###################################################################
def render_library_mode():
    """Book library: create, view, manage, read books."""
    st.markdown("### 📚 내 책장")
    show_copyright_extended()

    lib: list[Book] = st.session_state.book_library

    # -- Create new book section --
    with st.expander("📕 새 책 만들기", expanded=(len(lib) == 0)):
        title = st.text_input("책 제목", placeholder="나의 새 책", key="new_book_title")

        st.markdown("**페이지 추가 (이미지 여러 장)**")
        book_images = st.file_uploader(
            "이미지 파일을 올려주세요 (여러 장 가능)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="book_images_upload",
        )

        book_pdf = None
        if is_pdf_supported():
            st.markdown("**또는 PDF로 한번에 추가**")
            book_pdf = st.file_uploader(
                "PDF 파일을 올려주세요",
                type=["pdf"],
                key="book_pdf_upload",
            )

        if st.button("📖 책 만들기", key="create_book_btn", type="primary"):
            book_title = title.strip() if title.strip() else f"책 #{len(lib) + 1}"
            new_book = Book(title=book_title)

            pages_added = 0

            # Add images
            if book_images:
                for img_file in book_images:
                    img = Image.open(img_file)
                    new_book.add_page(img)
                    pages_added += 1

            # Add PDF pages
            if book_pdf is not None:
                pdf_bytes = book_pdf.read()
                with st.spinner("PDF 페이지를 읽는 중..."):
                    pdf_imgs = extract_pages_from_pdf(pdf_bytes)
                for pimg in pdf_imgs:
                    new_book.add_page(pimg)
                    pages_added += 1

            if pages_added > 0:
                add_book_to_library(st.session_state, new_book)
                st.success(f"'{book_title}' 책이 만들어졌어요! ({pages_added}페이지)")
                st.rerun()
            else:
                st.warning("페이지를 최소 1개 추가해 주세요!")

    # -- Library grid --
    if not lib:
        st.info("아직 책이 없어요. 위에서 새 책을 만들어 보세요!")
    else:
        st.markdown(f"**총 {len(lib)}권의 책**")

        cols_per_row = 3
        for row_start in range(0, len(lib), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                book_idx = row_start + col_idx
                if book_idx >= len(lib):
                    break
                b = lib[book_idx]
                with cols[col_idx]:
                    card_html = get_book_card_html(b, book_idx)
                    st.markdown(card_html, unsafe_allow_html=True)
                    col_read, col_del = st.columns(2)
                    with col_read:
                        if st.button("📖 읽기", key=f"read_book_{book_idx}"):
                            st.session_state.current_book_index = book_idx
                            st.session_state.audio_bytes = None
                            st.session_state.app_mode = "📖 읽기 모드"
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ 삭제", key=f"del_book_{book_idx}"):
                            remove_book_from_library(st.session_state, book_idx)
                            st.rerun()

    show_copyright()


# ###################################################################
#  MODE: 읽기 기록 (Reading History)
# ###################################################################
def render_history_mode():
    """Display reading history stored in session state."""
    st.markdown("### 📋 읽기 기록")

    # Phase 4: Stats dashboard at the top
    st.markdown(get_stats_css(), unsafe_allow_html=True)
    st.markdown(get_stats_component(), unsafe_allow_html=True)
    st.markdown("---")

    history = st.session_state.reading_history

    if not history:
        st.info("아직 읽기 기록이 없어요. 책을 읽으면 자동으로 저장됩니다!")
    else:
        st.markdown(f"**총 {len(history)}개의 기록**")
        for i, entry in enumerate(history):
            with st.container():
                st.markdown(
                    f'<div class="history-item">'
                    f'<b>🕐 {entry["time"]}</b><br>'
                    f'{entry["text_preview"]}'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                col_view, col_listen = st.columns(2)
                with col_view:
                    if st.button("📄 전체 보기", key=f"hist_view_{i}"):
                        st.session_state[f"_hist_expand_{i}"] = not st.session_state.get(f"_hist_expand_{i}", False)
                        st.rerun()
                if st.session_state.get(f"_hist_expand_{i}", False):
                    st.text_area(
                        "전체 텍스트",
                        value=entry["full_text"],
                        height=150,
                        key=f"hist_text_{i}",
                        disabled=True,
                    )
                with col_listen:
                    if st.button("🔊 듣기", key=f"hist_listen_{i}"):
                        with st.spinner("목소리를 만들고 있어요..."):
                            audio = synthesize_speech(
                                entry["full_text"],
                                speed="보통",
                                voice=st.session_state.voice,
                                lang_override=_tts_lang_override(),
                            )
                        html = get_audio_html(audio, autoplay=True, speed="보통")
                        st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ 기록 모두 삭제", key="clear_history"):
            st.session_state.reading_history = []
            st.rerun()

    show_copyright()


# ###################################################################
#  ROUTING
# ###################################################################

# Inject Phase 4 CSS and sound initialization (global)
st.markdown(get_rewards_css(), unsafe_allow_html=True)
st.markdown(get_sound_init_html(), unsafe_allow_html=True)

if st.session_state.app_mode == "📖 읽기 모드":
    render_reading_mode()
elif st.session_state.app_mode == "🎯 따라 읽기":
    render_readalong_mode()
elif st.session_state.app_mode == "📚 내 책장":
    render_library_mode()
elif st.session_state.app_mode == "📋 읽기 기록":
    render_history_mode()
else:
    render_reading_mode()

# Display buddy character at bottom right (default mood when not in read-along)
if st.session_state.app_mode not in ["🎯 따라 읽기"]:
    st.markdown(get_buddy_component(BuddyMood.DEFAULT), unsafe_allow_html=True)
