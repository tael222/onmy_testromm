"""STT module for ReadAlongBuddy - Speech-to-Text via Web Speech API."""

import streamlit.components.v1 as components


def get_stt_component(lang: str = "en-US") -> str:
    """Return HTML/JS component for Web Speech API speech recognition.

    This injects a JavaScript-based speech recognition UI into Streamlit.
    The recognized text is sent back to Streamlit via query params.

    Args:
        lang: BCP-47 language code (en-US, ko-KR, etc.)
    """
    html_code = f"""
    <div id="stt-container" style="text-align: center; padding: 1rem;">
        <button id="stt-btn" onclick="toggleRecording()"
                style="background-color: #FF6B6B; color: white; border: none;
                       border-radius: 50%; width: 80px; height: 80px; font-size: 2rem;
                       cursor: pointer; box-shadow: 0 4px 12px rgba(255,107,107,0.4);
                       transition: all 0.3s;">
            🎤
        </button>
        <p id="stt-status" style="margin-top: 0.5rem; color: #888; font-size: 1rem;">
            버튼을 눌러 말해보세요!
        </p>
        <div id="stt-result" style="margin-top: 1rem; padding: 0.8rem;
             background: #f0f8f0; border-radius: 12px; min-height: 40px;
             font-size: 1.1rem; display: none;">
        </div>
    </div>
    <script>
    let recognition = null;
    let isRecording = false;
    let finalTranscript = '';

    function checkSupport() {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            document.getElementById('stt-status').textContent =
                '이 브라우저는 음성 인식을 지원하지 않아요. Chrome을 사용해 주세요.';
            document.getElementById('stt-btn').disabled = true;
            document.getElementById('stt-btn').style.backgroundColor = '#ccc';
            return false;
        }}
        return true;
    }}

    function toggleRecording() {{
        if (!checkSupport()) return;

        if (isRecording) {{
            stopRecording();
        }} else {{
            startRecording();
        }}
    }}

    function startRecording() {{
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = '{lang}';
        recognition.interimResults = true;
        recognition.continuous = false;

        recognition.onstart = function() {{
            isRecording = true;
            document.getElementById('stt-btn').style.backgroundColor = '#4ECDC4';
            document.getElementById('stt-btn').textContent = '⏹';
            document.getElementById('stt-status').textContent = '듣고 있어요...';
            document.getElementById('stt-result').style.display = 'block';
            finalTranscript = '';
        }};

        recognition.onresult = function(event) {{
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript;
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            document.getElementById('stt-result').textContent = finalTranscript + interim;
        }};

        recognition.onend = function() {{
            isRecording = false;
            document.getElementById('stt-btn').style.backgroundColor = '#FF6B6B';
            document.getElementById('stt-btn').textContent = '🎤';
            document.getElementById('stt-status').textContent = '완료! 결과를 확인하세요.';

            // Send result back to Streamlit via window.parent
            if (finalTranscript) {{
                const data = {{stt_result: finalTranscript}};
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: data}}, '*');
            }}
        }};

        recognition.onerror = function(event) {{
            isRecording = false;
            document.getElementById('stt-btn').style.backgroundColor = '#FF6B6B';
            document.getElementById('stt-btn').textContent = '🎤';
            if (event.error === 'not-allowed') {{
                document.getElementById('stt-status').textContent = '마이크 권한이 필요해요!';
            }} else {{
                document.getElementById('stt-status').textContent = '다시 시도해 주세요.';
            }}
        }};

        recognition.start();
    }}

    function stopRecording() {{
        if (recognition) {{
            recognition.stop();
        }}
    }}

    checkSupport();
    </script>
    """
    return html_code


def render_stt_ui(lang: str = "en-US"):
    """Render the STT component in Streamlit.

    Args:
        lang: BCP-47 language code
    """
    html = get_stt_component(lang)
    components.html(html, height=250)
