"""Pronunciation feedback module for ReadAlongBuddy."""

import difflib


def calculate_similarity(original: str, spoken: str) -> float:
    """Calculate text similarity score between original and spoken text.

    Args:
        original: Original text from the book
        spoken: Text recognized from user's speech
    Returns:
        Similarity score from 0.0 to 1.0
    """
    original_lower = original.lower().strip()
    spoken_lower = spoken.lower().strip()

    if not original_lower or not spoken_lower:
        return 0.0

    return difflib.SequenceMatcher(None, original_lower, spoken_lower).ratio()


def get_word_comparison(original: str, spoken: str) -> list[dict]:
    """Compare words between original and spoken text.

    Returns list of dicts with keys: word, status ('correct', 'wrong', 'missing', 'extra')
    """
    orig_words = original.lower().strip().split()
    spoken_words = spoken.lower().strip().split()

    matcher = difflib.SequenceMatcher(None, orig_words, spoken_words)
    result = []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            for w in orig_words[i1:i2]:
                result.append({"word": w, "status": "correct"})
        elif op == 'replace':
            for w in orig_words[i1:i2]:
                result.append({"word": w, "status": "wrong"})
        elif op == 'delete':
            for w in orig_words[i1:i2]:
                result.append({"word": w, "status": "missing"})
        elif op == 'insert':
            for w in spoken_words[j1:j2]:
                result.append({"word": w, "status": "extra"})

    return result


def get_feedback_html(score: float, word_results: list[dict]) -> str:
    """Generate child-friendly HTML feedback.

    Args:
        score: similarity score (0.0 to 1.0)
        word_results: list from get_word_comparison
    """
    pct = int(score * 100)

    # Star rating (1-5)
    if pct >= 90:
        stars = "⭐⭐⭐⭐⭐"
        message = "완벽해요! 정말 잘 읽었어요! 🎉"
        color = "#4ECDC4"
    elif pct >= 70:
        stars = "⭐⭐⭐⭐"
        message = "잘했어요! 거의 다 맞았어요! 😊"
        color = "#82C91E"
    elif pct >= 50:
        stars = "⭐⭐⭐"
        message = "좋아요! 조금만 더 연습하면 완벽해요! 💪"
        color = "#FFD43B"
    elif pct >= 30:
        stars = "⭐⭐"
        message = "괜찮아요! 다시 한번 들어보고 따라해요! 📖"
        color = "#FF922B"
    else:
        stars = "⭐"
        message = "천천히 다시 해볼까요? 할 수 있어요! 🌟"
        color = "#FF6B6B"

    # Word-level display
    word_html_parts = []
    for item in word_results:
        w = item["word"]
        s = item["status"]
        if s == "correct":
            word_html_parts.append(f'<span style="color: #2ECC71; font-weight: bold;">{w}</span>')
        elif s == "wrong":
            word_html_parts.append(f'<span style="color: #E74C3C; text-decoration: underline wavy #E74C3C; font-weight: bold;">{w}</span>')
        elif s == "missing":
            word_html_parts.append(f'<span style="color: #E67E22; opacity: 0.7; font-style: italic;">[{w}]</span>')
        else:  # extra
            word_html_parts.append(f'<span style="color: #95A5A6; font-size: 0.9em;">({w})</span>')

    words_display = ' '.join(word_html_parts)

    html = f"""
    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 20px; padding: 1.5rem; margin: 1rem 0;
                border: 3px solid {color};">
        <div style="text-align: center; font-size: 2rem; margin-bottom: 0.5rem;">
            {stars}
        </div>
        <div style="text-align: center; font-size: 1.8rem; font-weight: bold;
                    color: {color}; margin-bottom: 0.5rem;">
            {pct}점
        </div>
        <div style="text-align: center; font-size: 1.2rem; color: #555; margin-bottom: 1rem;">
            {message}
        </div>
        <div style="background: white; border-radius: 12px; padding: 1rem;
                    font-size: 1.1rem; line-height: 2;">
            {words_display}
        </div>
        <div style="text-align: center; margin-top: 0.8rem; font-size: 0.85rem; color: #aaa;">
            🟢 맞은 단어 &nbsp; 🔴 틀린 단어 &nbsp; 🟠 빠진 단어
        </div>
    </div>
    """
    return html
