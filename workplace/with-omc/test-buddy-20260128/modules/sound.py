"""Sound module - Audio feedback for ReadAlongBuddy."""

import streamlit as st
import base64

# Sound enabled state
def init_sound_state():
    """Initialize sound state in session_state."""
    if "sound_enabled" not in st.session_state:
        st.session_state.sound_enabled = True

def is_sound_enabled() -> bool:
    """Check if sound is enabled."""
    init_sound_state()
    return st.session_state.sound_enabled

def toggle_sound():
    """Toggle sound on/off."""
    init_sound_state()
    st.session_state.sound_enabled = not st.session_state.sound_enabled

def get_sound_toggle_html() -> str:
    """Get HTML for sound toggle button."""
    enabled = is_sound_enabled()
    icon = "🔊" if enabled else "🔇"
    status = "켜짐" if enabled else "꺼짐"
    return f'{icon} 소리 {status}'

# Web Audio API based sound generation
def get_sound_script() -> str:
    """Get JavaScript for Web Audio API sound effects."""
    return '''
    <script>
    // Audio context for sound effects
    let audioCtx = null;

    function getAudioContext() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        return audioCtx;
    }

    // Star sound - cheerful ting
    function playStarSound() {
        if (!window.soundEnabled) return;
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
        osc.frequency.setValueAtTime(1760, ctx.currentTime + 0.1); // A6

        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.3);
    }

    // Badge/celebration sound - fanfare
    function playBadgeSound() {
        if (!window.soundEnabled) return;
        const ctx = getAudioContext();

        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
        const duration = 0.15;

        notes.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(0.2, ctx.currentTime + i * duration);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * duration + duration);

            osc.start(ctx.currentTime + i * duration);
            osc.stop(ctx.currentTime + i * duration + duration + 0.1);
        });
    }

    // Correct answer sound - pleasant chime
    function playCorrectSound() {
        if (!window.soundEnabled) return;
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.type = 'sine';
        osc.frequency.setValueAtTime(659.25, ctx.currentTime); // E5
        osc.frequency.setValueAtTime(783.99, ctx.currentTime + 0.1); // G5

        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.25);
    }

    // Encouraging sound - gentle tone
    function playEncouragingSound() {
        if (!window.soundEnabled) return;
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, ctx.currentTime); // A4

        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.2);
    }

    // Level up sound - triumphant
    function playLevelUpSound() {
        if (!window.soundEnabled) return;
        const ctx = getAudioContext();

        const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99]; // C4 to G5
        const duration = 0.1;

        notes.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(0.2, ctx.currentTime + i * duration);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * duration + duration * 2);

            osc.start(ctx.currentTime + i * duration);
            osc.stop(ctx.currentTime + i * duration + duration * 2);
        });
    }

    // Initialize sound state from Streamlit
    window.soundEnabled = true;
    </script>
    '''

def play_star_sound() -> str:
    """Return HTML/JS to play star sound."""
    if not is_sound_enabled():
        return ""
    return '<script>playStarSound();</script>'

def play_badge_sound() -> str:
    """Return HTML/JS to play badge sound."""
    if not is_sound_enabled():
        return ""
    return '<script>playBadgeSound();</script>'

def play_correct_sound() -> str:
    """Return HTML/JS to play correct sound."""
    if not is_sound_enabled():
        return ""
    return '<script>playCorrectSound();</script>'

def play_encouraging_sound() -> str:
    """Return HTML/JS to play encouraging sound."""
    if not is_sound_enabled():
        return ""
    return '<script>playEncouragingSound();</script>'

def play_level_up_sound() -> str:
    """Return HTML/JS to play level up sound."""
    if not is_sound_enabled():
        return ""
    return '<script>playLevelUpSound();</script>'

def get_sound_init_html() -> str:
    """Get complete sound initialization HTML with scripts."""
    enabled = is_sound_enabled()
    return get_sound_script() + f'''
    <script>
    window.soundEnabled = {'true' if enabled else 'false'};
    </script>
    '''
