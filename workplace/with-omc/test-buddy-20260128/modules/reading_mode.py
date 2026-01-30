"""Reading mode module - sentence-by-sentence TTS with highlighting."""

import re


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation (. ! ? and Korean 。)."""
    # Split on .!? followed by space or end, preserving delimiters
    sentences = re.split(r'(?<=[.!?。])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def get_highlighted_text_html(sentences: list[str], current_index: int) -> str:
    """Generate HTML with current sentence highlighted in yellow/green.

    Args:
        sentences: list of sentence strings
        current_index: index of currently active sentence (-1 for none)
    Returns:
        HTML string with highlighted sentence
    """
    parts = []
    for i, sentence in enumerate(sentences):
        if i == current_index:
            parts.append(
                f'<span style="background-color: #FFE66D; padding: 2px 6px; '
                f'border-radius: 8px; font-weight: bold; font-size: 1.2rem;">'
                f'{sentence}</span>'
            )
        else:
            parts.append(
                f'<span style="color: #555; font-size: 1.1rem;">{sentence}</span>'
            )
    return '<div style="line-height: 2.2; padding: 1rem;">' + ' '.join(parts) + '</div>'


def get_word_highlighted_html(sentence: str, words_per_group: int = 3) -> str:
    """Generate HTML for word-level highlight display of a single sentence.

    Returns HTML where each word group can be individually highlighted via JS.
    """
    words = sentence.split()
    parts = []
    for i, word in enumerate(words):
        parts.append(f'<span id="word-{i}" style="font-size: 1.2rem; padding: 1px 3px;">{word}</span>')
    return '<div style="line-height: 2.2; padding: 1rem;">' + ' '.join(parts) + '</div>'
