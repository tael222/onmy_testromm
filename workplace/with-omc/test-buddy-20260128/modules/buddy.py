"""Buddy module - Reading companion character system for ReadAlongBuddy."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random

class BuddyMood(Enum):
    """Buddy character mood/expression states."""
    DEFAULT = "default"
    HAPPY = "happy"
    ENCOURAGING = "encouraging"
    CELEBRATING = "celebrating"
    THINKING = "thinking"

# Emoji-based character expressions
BUDDY_EXPRESSIONS = {
    BuddyMood.DEFAULT: "🐻",
    BuddyMood.HAPPY: "🐻",
    BuddyMood.ENCOURAGING: "🐻",
    BuddyMood.CELEBRATING: "🎉🐻🎉",
    BuddyMood.THINKING: "🤔🐻",
}

# Messages for each mood (Korean)
BUDDY_MESSAGES = {
    BuddyMood.DEFAULT: [
        "안녕! 같이 읽어볼까? 📚",
        "오늘도 재미있게 읽어보자!",
        "책 읽을 준비 됐어?",
    ],
    BuddyMood.HAPPY: [
        "와! 정말 잘 읽었어! ⭐",
        "대단해! 멋지다!",
        "훌륭해! 계속 이렇게!",
        "짝짝짝! 👏",
    ],
    BuddyMood.ENCOURAGING: [
        "조금만 더 힘내! 💪",
        "괜찮아, 다시 해보자!",
        "천천히 읽어도 괜찮아~",
        "실수해도 괜찮아! 다시 도전!",
        "할 수 있어! 화이팅!",
    ],
    BuddyMood.CELEBRATING: [
        "우와~! 대단해! 🎊",
        "축하해! 레벨업! 🌟",
        "너무 잘했어! 최고야!",
        "와아! 새 배지 획득! 🏆",
    ],
    BuddyMood.THINKING: [
        "음... 이 단어는 어떻게 읽을까?",
        "한번 들어볼까?",
        "천천히 생각해봐~",
    ],
}

@dataclass
class BuddyState:
    """Current state of the buddy character."""
    mood: BuddyMood = BuddyMood.DEFAULT
    message: str = ""
    show_animation: bool = False
    animation_type: str = "bounce"

def get_buddy_message(mood: BuddyMood) -> str:
    """Get a random message for the given mood."""
    messages = BUDDY_MESSAGES.get(mood, BUDDY_MESSAGES[BuddyMood.DEFAULT])
    return random.choice(messages)

def get_buddy_expression(mood: BuddyMood) -> str:
    """Get the emoji expression for the given mood."""
    return BUDDY_EXPRESSIONS.get(mood, BUDDY_EXPRESSIONS[BuddyMood.DEFAULT])

def get_mood_for_accuracy(accuracy: float) -> BuddyMood:
    """Determine buddy mood based on reading accuracy."""
    if accuracy >= 90:
        return BuddyMood.CELEBRATING
    elif accuracy >= 70:
        return BuddyMood.HAPPY
    elif accuracy >= 50:
        return BuddyMood.ENCOURAGING
    else:
        return BuddyMood.ENCOURAGING  # Always encouraging, never negative

def get_buddy_css() -> str:
    """Return CSS for buddy character animations."""
    return """
    <style>
    .buddy-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    .buddy-character {
        font-size: 4rem;
        animation: buddy-bounce 2s ease-in-out infinite;
        cursor: pointer;
        transition: transform 0.3s ease;
    }

    .buddy-character:hover {
        transform: scale(1.1);
    }

    .buddy-character.celebrating {
        animation: buddy-celebrate 0.5s ease-in-out infinite;
    }

    .buddy-character.encouraging {
        animation: buddy-wave 1s ease-in-out infinite;
    }

    .buddy-speech-bubble {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFECD2 100%);
        border-radius: 20px;
        padding: 12px 18px;
        max-width: 200px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
        animation: bubble-appear 0.3s ease-out;
        font-size: 1rem;
        color: #5D4E37;
        text-align: center;
    }

    .buddy-speech-bubble::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 10px 10px 0;
        border-style: solid;
        border-color: #FFECD2 transparent transparent;
    }

    @keyframes buddy-bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    @keyframes buddy-celebrate {
        0%, 100% { transform: rotate(-5deg) scale(1); }
        25% { transform: rotate(5deg) scale(1.1); }
        50% { transform: rotate(-5deg) scale(1); }
        75% { transform: rotate(5deg) scale(1.1); }
    }

    @keyframes buddy-wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-10deg); }
        75% { transform: rotate(10deg); }
    }

    @keyframes bubble-appear {
        0% { opacity: 0; transform: scale(0.8) translateY(10px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    </style>
    """

def render_buddy_html(mood: BuddyMood, message: Optional[str] = None) -> str:
    """Render the buddy character as HTML with speech bubble."""
    if message is None:
        message = get_buddy_message(mood)

    expression = get_buddy_expression(mood)
    animation_class = mood.value if mood in [BuddyMood.CELEBRATING, BuddyMood.ENCOURAGING] else ""

    return f"""
    <div class="buddy-container">
        <div class="buddy-speech-bubble">{message}</div>
        <div class="buddy-character {animation_class}">{expression}</div>
    </div>
    """

def get_buddy_component(mood: BuddyMood = BuddyMood.DEFAULT, message: Optional[str] = None) -> str:
    """Get complete buddy component HTML with CSS."""
    css = get_buddy_css()
    html = render_buddy_html(mood, message)
    return css + html
