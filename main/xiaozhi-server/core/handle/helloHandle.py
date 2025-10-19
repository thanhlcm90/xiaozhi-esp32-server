import time
import json
import random
import asyncio
from core.utils.dialogue import Message
from core.utils.util import audio_to_data
from core.providers.tts.dto.dto import SentenceType
from core.utils.wakeup_word import WakeupWordsConfig
from core.handle.sendAudioHandle import sendAudioMessage, send_tts_message
from core.utils.util import remove_punctuation_and_length, opus_datas_to_wav_bytes
from core.providers.tools.device_mcp import (
    MCPClient,
    send_mcp_initialize_message,
    send_mcp_tools_list_request,
)

TAG = __name__

WAKEUP_CONFIG = {
    "refresh_time": 10,
    "responses": [
        "I'm here, please say.",
        "I'm here, please tell me.",
        "Here I am, please tell me.",
        "Please tell me.",
        "Please speak.",
        "Please tell me the command.",
        "I'm listening.",
        "Please help me.",
        "I'm here, please wait for your command.",
    ],
}

# Create global wakeup word configuration manager
wakeup_words_config = WakeupWordsConfig()

# Used to prevent concurrent calls to wakeupWordsResponse
_wakeup_response_lock = asyncio.Lock()


async def handleHelloMessage(conn, msg_json):
    """Handle hello message"""
    audio_params = msg_json.get("audio_params")
    if audio_params:
        format = audio_params.get("format")
        conn.logger.bind(tag=TAG).info(f"Client audio format: {format}")
        conn.audio_format = format
        conn.welcome_msg["audio_params"] = audio_params
    features = msg_json.get("features")
    if features:
        conn.logger.bind(tag=TAG).info(f"Client features: {features}")
        conn.features = features
        if features.get("mcp"):
            conn.logger.bind(tag=TAG).info("Client supports MCP")
            conn.mcp_client = MCPClient()
            # Send initialization
            asyncio.create_task(send_mcp_initialize_message(conn))
            # Send mcp message, get tools list
            asyncio.create_task(send_mcp_tools_list_request(conn))

    await conn.websocket.send(json.dumps(conn.welcome_msg))


async def checkWakeupWords(conn, text):
    enable_wakeup_words_response_cache = conn.config[
        "enable_wakeup_words_response_cache"
    ]

    # Wait for tts initialization, up to 3 seconds
    start_time = time.time()
    while time.time() - start_time < 3:
        if conn.tts:
            break
        await asyncio.sleep(0.1)
    else:
        return False

    if not enable_wakeup_words_response_cache:
        return False

    _, filtered_text = remove_punctuation_and_length(text)
    if filtered_text not in conn.config.get("wakeup_words"):
        return False

    conn.just_woken_up = True
    await send_tts_message(conn, "start")

    # Get current voice
    voice = getattr(conn.tts, "voice", "default")
    if not voice:
        voice = "default"

    # Get wakeup word reply configuration
    response = wakeup_words_config.get_wakeup_response(voice)
    if not response or not response.get("file_path"):
        response = {
            "voice": "default",
            "file_path": "config/assets/wakeup_words_short.wav",
            "time": 0,
            "text": "I'm here!",
        }

    # Get audio data
    opus_packets = audio_to_data(response.get("file_path"))
    # Play wakeup word reply
    conn.client_abort = False

    conn.logger.bind(tag=TAG).info(f"Play wakeup word reply: {response.get('text')}")
    await sendAudioMessage(conn, SentenceType.FIRST, opus_packets, response.get("text"))
    await sendAudioMessage(conn, SentenceType.LAST, [], None)

    # Supplement dialogue
    conn.dialogue.put(Message(role="assistant", content=response.get("text")))

    # Check if update wakeup word reply is needed
    if time.time() - response.get("time", 0) > WAKEUP_CONFIG["refresh_time"]:
        if not _wakeup_response_lock.locked():
            asyncio.create_task(wakeupWordsResponse(conn))
    return True


async def wakeupWordsResponse(conn):
    if not conn.tts:
        return

    try:
        # Try to acquire lock, if not available return
        if not await _wakeup_response_lock.acquire():
            return

        # Randomly select a reply from predefined reply list
        result = random.choice(WAKEUP_CONFIG["responses"])
        if not result or len(result) == 0:
            return

        # Generate TTS audio
        tts_result = await asyncio.to_thread(conn.tts.to_tts, result)
        if not tts_result:
            return

        # Get current voice
        voice = getattr(conn.tts, "voice", "default")

        wav_bytes = opus_datas_to_wav_bytes(tts_result, sample_rate=16000)
        file_path = wakeup_words_config.generate_file_path(voice)
        with open(file_path, "wb") as f:
            f.write(wav_bytes)
        # Update configuration
        wakeup_words_config.update_wakeup_response(voice, file_path, result)
    finally:
        # Ensure lock is released in all cases
        if _wakeup_response_lock.locked():
            _wakeup_response_lock.release()
