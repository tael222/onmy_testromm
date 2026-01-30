"""TTS module for ReadAlongBuddy - text to speech conversion."""

import io
import base64
import uuid
from gtts import gTTS

SPEED_MAP = {
    "느리게": True,
    "보통": False,
    "빠르게": False,
}

PLAYBACK_RATE = {
    "느리게": 0.75,
    "보통": 1.0,
    "빠르게": 1.5,
}

# Voice options: display_name -> (gTTS lang, gTTS tld)
VOICE_OPTIONS = {
    "English (US)": ("en", "com"),
    "English (UK)": ("en", "co.uk"),
    "English (AU)": ("en", "com.au"),
    "English (IN)": ("en", "co.in"),
    "한국어": ("ko", "com"),
}

DEFAULT_VOICE = "English (US)"


def get_voice_list() -> list[str]:
    """Return list of available voice display names."""
    return list(VOICE_OPTIONS.keys())


def synthesize_speech(text: str, speed: str = "보통", voice: str = DEFAULT_VOICE, lang_override: str | None = None) -> bytes:
    """Convert text to speech audio bytes using gTTS.

    Args:
        text: Text to synthesize
        speed: Speed label (느리게/보통/빠르게)
        voice: Voice display name from VOICE_OPTIONS
        lang_override: Override language code directly (e.g., 'ko' for Korean)
    """
    slow = SPEED_MAP.get(speed, False)

    if lang_override:
        lang = lang_override
        tld = "com"
    else:
        lang, tld = VOICE_OPTIONS.get(voice, ("en", "com"))

    tts = gTTS(text=text, lang=lang, slow=slow, tld=tld)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


def get_audio_html(audio_bytes: bytes, autoplay: bool = False, speed: str = "보통", audio_id: str | None = None) -> str:
    """Generate HTML audio element with playback speed control.

    Args:
        audio_bytes: MP3 audio data
        autoplay: Whether to autoplay
        speed: Speed label for playback rate
        audio_id: Custom audio element ID (unique per instance)
    """
    b64 = base64.b64encode(audio_bytes).decode()
    autoplay_attr = "autoplay" if autoplay else ""
    rate = PLAYBACK_RATE.get(speed, 1.0)
    if audio_id is None:
        audio_id = f"rab-audio-{uuid.uuid4().hex[:8]}"
    return (
        f'<audio id="{audio_id}" controls {autoplay_attr} style="width:100%">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        f'<script>document.getElementById("{audio_id}").playbackRate={rate};</script>'
    )


def synthesize_sentence(text: str, speed: str = "보통", voice: str = DEFAULT_VOICE, lang_override: str | None = None) -> bytes:
    """Synthesize a single sentence (alias for synthesize_speech, for clarity)."""
    return synthesize_speech(text, speed=speed, voice=voice, lang_override=lang_override)
