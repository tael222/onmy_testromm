"""Rewards module - Stars, badges, and level system for ReadAlongBuddy."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
import streamlit as st

class Level(Enum):
    """Reading level progression."""
    SPROUT = ("새싹", "🌱", 0)
    LITTLE_READER = ("꼬마독서가", "📖", 10)
    READING_KING = ("독서왕", "👑", 50)
    MASTER = ("마스터", "🎓", 100)
    LEGEND = ("전설", "⭐", 200)

    def __init__(self, korean_name: str, emoji: str, stars_required: int):
        self.korean_name = korean_name
        self.emoji = emoji
        self.stars_required = stars_required

@dataclass
class Badge:
    """Achievement badge."""
    id: str
    name: str
    description: str
    emoji: str
    unlocked: bool = False

# Available badges
BADGES = {
    "first_book": Badge("first_book", "첫 책 읽기", "첫 번째 책을 읽었어요!", "📚"),
    "star_collector_10": Badge("star_collector_10", "별 수집가", "별 10개를 모았어요!", "⭐"),
    "star_collector_50": Badge("star_collector_50", "별 마스터", "별 50개를 모았어요!", "🌟"),
    "star_collector_100": Badge("star_collector_100", "별 전설", "별 100개를 모았어요!", "💫"),
    "perfect_sentence": Badge("perfect_sentence", "완벽한 문장", "문장을 완벽하게 읽었어요!", "✨"),
    "five_streak": Badge("five_streak", "5연속 성공", "5문장 연속 성공!", "🔥"),
    "ten_pages": Badge("ten_pages", "10페이지 돌파", "10페이지를 읽었어요!", "📄"),
    "level_up": Badge("level_up", "레벨업!", "레벨이 올랐어요!", "🆙"),
}

@dataclass
class RewardState:
    """Current reward state for a session."""
    total_stars: int = 0
    session_stars: int = 0
    current_level: Level = Level.SPROUT
    unlocked_badges: List[str] = field(default_factory=list)
    pages_read: int = 0
    sentences_read: int = 0
    perfect_sentences: int = 0
    current_streak: int = 0
    best_streak: int = 0
    books_completed: int = 0

def init_reward_state():
    """Initialize reward state in session_state."""
    if "rewards" not in st.session_state:
        st.session_state.rewards = RewardState()

def get_reward_state() -> RewardState:
    """Get current reward state."""
    init_reward_state()
    return st.session_state.rewards

def calculate_stars(accuracy: float) -> int:
    """Calculate stars earned based on accuracy percentage."""
    if accuracy >= 95:
        return 3
    elif accuracy >= 85:
        return 2
    elif accuracy >= 70:
        return 1
    return 0

def award_stars(accuracy: float) -> tuple[int, List[Badge]]:
    """Award stars and check for new badges. Returns (stars_earned, new_badges)."""
    state = get_reward_state()
    stars = calculate_stars(accuracy)
    new_badges = []

    if stars > 0:
        state.total_stars += stars
        state.session_stars += stars
        state.sentences_read += 1

        # Perfect sentence
        if accuracy >= 95:
            state.perfect_sentences += 1
            state.current_streak += 1
            if state.current_streak > state.best_streak:
                state.best_streak = state.current_streak

            # Check perfect sentence badge
            if "perfect_sentence" not in state.unlocked_badges:
                state.unlocked_badges.append("perfect_sentence")
                new_badges.append(BADGES["perfect_sentence"])
        else:
            state.current_streak = 0

        # Check streak badge
        if state.current_streak >= 5 and "five_streak" not in state.unlocked_badges:
            state.unlocked_badges.append("five_streak")
            new_badges.append(BADGES["five_streak"])

        # Check star collection badges
        if state.total_stars >= 10 and "star_collector_10" not in state.unlocked_badges:
            state.unlocked_badges.append("star_collector_10")
            new_badges.append(BADGES["star_collector_10"])
        if state.total_stars >= 50 and "star_collector_50" not in state.unlocked_badges:
            state.unlocked_badges.append("star_collector_50")
            new_badges.append(BADGES["star_collector_50"])
        if state.total_stars >= 100 and "star_collector_100" not in state.unlocked_badges:
            state.unlocked_badges.append("star_collector_100")
            new_badges.append(BADGES["star_collector_100"])

        # Check level up
        old_level = state.current_level
        state.current_level = get_level_for_stars(state.total_stars)
        if state.current_level != old_level and "level_up" not in state.unlocked_badges:
            state.unlocked_badges.append("level_up")
            new_badges.append(BADGES["level_up"])
    else:
        state.current_streak = 0

    return stars, new_badges

def record_page_read():
    """Record a page being read."""
    state = get_reward_state()
    state.pages_read += 1

    new_badges = []
    if state.pages_read >= 10 and "ten_pages" not in state.unlocked_badges:
        state.unlocked_badges.append("ten_pages")
        new_badges.append(BADGES["ten_pages"])

    return new_badges

def record_book_completed():
    """Record a book being completed."""
    state = get_reward_state()
    state.books_completed += 1

    new_badges = []
    if state.books_completed >= 1 and "first_book" not in state.unlocked_badges:
        state.unlocked_badges.append("first_book")
        new_badges.append(BADGES["first_book"])

    return new_badges

def get_level_for_stars(stars: int) -> Level:
    """Get level based on total stars."""
    for level in reversed(list(Level)):
        if stars >= level.stars_required:
            return level
    return Level.SPROUT

def get_progress_to_next_level(state: RewardState) -> tuple[int, int, float]:
    """Get progress to next level. Returns (current_stars, next_level_stars, percentage)."""
    levels = list(Level)
    current_idx = levels.index(state.current_level)

    if current_idx >= len(levels) - 1:
        return state.total_stars, state.total_stars, 100.0

    next_level = levels[current_idx + 1]
    current_threshold = state.current_level.stars_required
    next_threshold = next_level.stars_required

    progress = state.total_stars - current_threshold
    needed = next_threshold - current_threshold
    percentage = min(100.0, (progress / needed) * 100)

    return progress, needed, percentage

def get_rewards_css() -> str:
    """Return CSS for rewards animations."""
    return """
    <style>
    .star-display {
        font-size: 2rem;
        display: inline-flex;
        gap: 5px;
        animation: star-appear 0.5s ease-out;
    }

    .star-earned {
        animation: star-pop 0.6s ease-out;
        display: inline-block;
    }

    .star-empty {
        opacity: 0.3;
    }

    .level-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .badge-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 30px 50px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 2000;
        text-align: center;
        animation: badge-celebrate 0.5s ease-out;
    }

    .badge-popup h2 {
        margin: 0;
        font-size: 2rem;
        color: #5D4E37;
    }

    .badge-popup .emoji {
        font-size: 4rem;
        margin: 10px 0;
    }

    .progress-bar-container {
        width: 100%;
        height: 20px;
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }

    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.5s ease-out;
    }

    @keyframes star-pop {
        0% { transform: scale(0); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }

    @keyframes star-appear {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes badge-celebrate {
        0% { transform: translate(-50%, -50%) scale(0) rotate(-10deg); }
        50% { transform: translate(-50%, -50%) scale(1.1) rotate(5deg); }
        100% { transform: translate(-50%, -50%) scale(1) rotate(0deg); }
    }
    </style>
    """

def render_stars_html(stars_earned: int, max_stars: int = 3) -> str:
    """Render stars as HTML."""
    stars_html = ""
    for i in range(max_stars):
        if i < stars_earned:
            delay = i * 0.2
            stars_html += f'<span class="star-earned" style="animation-delay: {delay}s">⭐</span>'
        else:
            stars_html += '<span class="star-empty">⭐</span>'
    return f'<div class="star-display">{stars_html}</div>'

def render_level_badge_html(level: Level) -> str:
    """Render level badge as HTML."""
    return f'''
    <div class="level-badge">
        <span>{level.emoji}</span>
        <span>{level.korean_name}</span>
    </div>
    '''

def render_badge_popup_html(badge: Badge) -> str:
    """Render badge unlock popup as HTML."""
    return f'''
    <div class="badge-popup">
        <div class="emoji">{badge.emoji}</div>
        <h2>{badge.name}</h2>
        <p>{badge.description}</p>
    </div>
    '''

def render_progress_bar_html(percentage: float, label: str = "") -> str:
    """Render progress bar as HTML."""
    return f'''
    <div>
        <small>{label}</small>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {percentage}%"></div>
        </div>
    </div>
    '''

def get_total_stars_display() -> str:
    """Get HTML for total stars in header."""
    state = get_reward_state()
    return f'⭐ {state.total_stars}'
