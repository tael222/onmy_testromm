"""Stats module - Progress tracking and dashboard for ReadAlongBuddy."""

from dataclasses import dataclass
from typing import Optional
import streamlit as st
from datetime import datetime

@dataclass
class SessionStats:
    """Statistics for current reading session."""
    session_start: datetime
    pages_read: int = 0
    sentences_read: int = 0
    words_read: int = 0
    total_accuracy: float = 0.0
    accuracy_count: int = 0
    time_spent_seconds: int = 0

def init_stats():
    """Initialize stats in session_state."""
    if "stats" not in st.session_state:
        st.session_state.stats = SessionStats(session_start=datetime.now())

def get_stats() -> SessionStats:
    """Get current session stats."""
    init_stats()
    return st.session_state.stats

def record_reading(sentence: str, accuracy: float):
    """Record a sentence being read with accuracy."""
    stats = get_stats()
    stats.sentences_read += 1
    words = len(sentence.split())
    stats.words_read += words
    stats.total_accuracy += accuracy
    stats.accuracy_count += 1

def record_page():
    """Record a page being read."""
    stats = get_stats()
    stats.pages_read += 1

def get_average_accuracy() -> float:
    """Get average accuracy for the session."""
    stats = get_stats()
    if stats.accuracy_count == 0:
        return 0.0
    return stats.total_accuracy / stats.accuracy_count

def get_session_duration_minutes() -> int:
    """Get session duration in minutes."""
    stats = get_stats()
    delta = datetime.now() - stats.session_start
    return int(delta.total_seconds() / 60)

def get_stats_css() -> str:
    """Return CSS for stats dashboard."""
    return """
    <style>
    .stats-dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        padding: 20px;
    }

    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);
    }

    .stat-card.highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 5px 0;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    .stats-header {
        text-align: center;
        margin-bottom: 20px;
    }

    .stats-header h2 {
        color: #5D4E37;
        margin: 0;
    }

    .achievement-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 10px;
        padding: 15px;
    }

    .achievement-item {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .achievement-item.unlocked {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    }

    .achievement-item.locked {
        opacity: 0.5;
        filter: grayscale(100%);
    }

    .achievement-emoji {
        font-size: 2rem;
    }

    .achievement-name {
        font-size: 0.8rem;
        margin-top: 5px;
        font-weight: 500;
    }
    </style>
    """

def render_stat_card(icon: str, value: str, label: str, highlight: bool = False) -> str:
    """Render a single stat card."""
    highlight_class = "highlight" if highlight else ""
    return f'''
    <div class="stat-card {highlight_class}">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    '''

def render_stats_dashboard_html() -> str:
    """Render the complete stats dashboard."""
    stats = get_stats()
    avg_accuracy = get_average_accuracy()
    duration = get_session_duration_minutes()

    # Import rewards to get star count
    try:
        from modules.rewards import get_reward_state, get_progress_to_next_level
        rewards = get_reward_state()
        total_stars = rewards.total_stars
        level_name = f"{rewards.current_level.emoji} {rewards.current_level.korean_name}"
        progress, needed, percentage = get_progress_to_next_level(rewards)
        badges_count = len(rewards.unlocked_badges)
    except ImportError:
        total_stars = 0
        level_name = "🌱 새싹"
        progress, needed, percentage = 0, 10, 0
        badges_count = 0

    dashboard_html = f'''
    <div class="stats-header">
        <h2>📊 오늘의 읽기 현황</h2>
    </div>
    <div class="stats-dashboard">
        {render_stat_card("⭐", str(total_stars), "모은 별", highlight=True)}
        {render_stat_card("📄", str(stats.pages_read), "읽은 페이지")}
        {render_stat_card("💬", str(stats.sentences_read), "읽은 문장")}
        {render_stat_card("📝", str(stats.words_read), "읽은 단어")}
        {render_stat_card("🎯", f"{avg_accuracy:.0f}%", "평균 정확도")}
        {render_stat_card("⏱️", f"{duration}분", "읽은 시간")}
        {render_stat_card("🏆", str(badges_count), "획득 배지")}
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <div class="level-badge" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">
            현재 레벨: {level_name}
        </div>
        <div style="margin-top: 10px;">
            <small>다음 레벨까지: {progress}/{needed} ⭐ ({percentage:.0f}%)</small>
            <div style="width: 200px; margin: 10px auto; height: 10px; background: #e0e0e0; border-radius: 5px; overflow: hidden;">
                <div style="height: 100%; width: {percentage}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 5px;"></div>
            </div>
        </div>
    </div>
    '''

    return dashboard_html

def render_achievement_grid_html() -> str:
    """Render the achievement/badge collection grid."""
    try:
        from modules.rewards import BADGES, get_reward_state
        rewards = get_reward_state()
        unlocked = rewards.unlocked_badges
    except ImportError:
        from modules.rewards import BADGES
        unlocked = []

    items_html = ""
    for badge_id, badge in BADGES.items():
        is_unlocked = badge_id in unlocked
        status_class = "unlocked" if is_unlocked else "locked"
        items_html += f'''
        <div class="achievement-item {status_class}">
            <div class="achievement-emoji">{badge.emoji}</div>
            <div class="achievement-name">{badge.name}</div>
        </div>
        '''

    return f'''
    <div class="stats-header" style="margin-top: 30px;">
        <h2>🏆 배지 컬렉션</h2>
    </div>
    <div class="achievement-grid">
        {items_html}
    </div>
    '''

def get_stats_component() -> str:
    """Get complete stats component with CSS."""
    css = get_stats_css()
    dashboard = render_stats_dashboard_html()
    achievements = render_achievement_grid_html()
    return css + dashboard + achievements
