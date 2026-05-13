"""
Claude в боте делает ТОЛЬКО две вещи:
1) parse_intent — извлекает структурированный intent из свободного текста менеджера
2) generate_copy — пишет креативную часть (название цвета, описание материала, цитата, benefits)

Вся арифметика — в calculator.py. Math ≠ LLM.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime

from anthropic import AsyncAnthropic

from catalog import SYSTEMS, all_systems_list

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"No JSON found in response: {text[:200]!r}")


# ─────────────────────────────────────────────────────────────
# PARSE INTENT
# ─────────────────────────────────────────────────────────────

_SYSTEM_LIST_TEXT = ", ".join(all_systems_list())

PARSE_PROMPT = f"""You extract a structured intent from a Pratta Thailand employee's request describing what a client wants. Output STRICT JSON only. No math, no prices, no calculations.

ALLOWED `system` values (use the exact id):
{_SYSTEM_LIST_TEXT}

Notes on mapping common names (be tolerant to typos / speech-to-text distortions):
- "travertino" / "travertin" / "травертин" / "имерум" / "imperium" → travertino_imperium
- "venetian" / "venetsian" / "венецианка" / "антико" → antico_veneziano
- "marmorino" / "мармарин" / "carrara" / "кеара" → marmorino_carrara (unless explicitly Antico Veneziano)
- "silk line" — pick the specific product the user named (seta_exclusive, antico_velluto, etc.)
- PAINTS — be especially tolerant to STT distortions:
    "plastogum" / "пластогум" / "пластагум" / "ластагам" / "lastagam" / "plastagum" / "пластик" / "эластомер"
    → plastogum
    A bare "краска" / "paint" with no other product name → plastogum (our hero paint)
    "theia" / "тея" / "тэя" / "egshell" → theia
    "int est" / "int&est" / "интест" → int_est
- If the request mentions BOTH a plaster system AND a paint ("manu + плюс плагостум на потолок") — pick the PRIMARY product (the one with more m² or mentioned first). The bot handles one system per KP.
- If the input is clearly a paint name even slightly distorted — map to the closest paint system. Do NOT return null.

OUTPUT JSON SCHEMA — every field required (use null where unknown):

{{
  "system": "<one of the allowed ids>",
  "area": <number in m², required>,
  "zone": "Interior" | "Exterior" | "Wet zone",
  "color_type": "light" | "dark",
  "color_name": "<short evocative English name like Warm Ivory, Deep Graphite, Soft Sand — or null if not specified>",
  "finish": "metalline_gold" | "metalline_silver" | "metalline_bronze" | "specchio_cera" | "velatura" | "umbrella" | "umbrella_silk" | null,
  "grade": "intonachino_fine" | "intonachino_medium" | "intonachino_coarse" | null,
  "application_included": true | false,
  "client_name": "<string or null>",
  "colorant_included": true | false
}}

Rules:
- If user says "светлый/light/light tone" → color_type: "light"
- If user says "тёмный/dark/глубокий" → color_type: "dark"
- Default zone: "Interior"
- Default color_type: "light"
- Default application_included: true if user says "с нанесением/with works/under turnkey/под ключ", false if "только материал/only material/самонанесение". If unclear → true.
- Default colorant_included: true (we always tint)
- Do NOT calculate or output prices — just intent.

OUTPUT ONLY THE JSON OBJECT, no other text."""


async def parse_intent(user_input: str) -> dict:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=PARSE_PROMPT,
        messages=[{"role": "user", "content": user_input}],
    )
    raw = response.content[0].text
    return _extract_json(raw)


# ─────────────────────────────────────────────────────────────
# REFINE INTENT — итеративная правка
# ─────────────────────────────────────────────────────────────

REFINE_PROMPT = """You take a previous intent JSON and a refinement message from the employee. Return a NEW intent JSON with the changes applied. Keep all unchanged fields the same. Output JSON only.

Possible refinements:
- "увеличь до X м²" / "make it X sqm" → update area
- "замени финиш на silver" / "use silver" → update finish to metalline_silver
- "пусть будет тёмный" / "switch to dark" → color_type: dark
- "без нанесения" / "material only" → application_included: false
- "имя клиента Ivan Petrov" → client_name
- "добавь зону мокрая" → zone: "Wet zone"

Output the FULL updated intent JSON (all fields), not just the changed ones."""


async def refine_intent(prev_intent: dict, refinement_text: str) -> dict:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=REFINE_PROMPT,
        messages=[
            {"role": "user", "content": f"Previous intent:\n{json.dumps(prev_intent, ensure_ascii=False)}"},
            {"role": "assistant", "content": "Understood. What's the change?"},
            {"role": "user", "content": refinement_text},
        ],
    )
    raw = response.content[0].text
    return _extract_json(raw)


# ─────────────────────────────────────────────────────────────
# GENERATE COPY — креативная часть для PDF
# ─────────────────────────────────────────────────────────────

COPY_PROMPT = """You write elegant English marketing copy for a Pratta Thailand commercial proposal PDF. Premium tone, restrained luxury — short, evocative, never salesy.

You receive a structured spec and return JSON with creative fields. Output JSON only.

INPUT will contain: product_title, chemistry, zone, color_type, color_name (may be null), tool.

OUTPUT:
{
  "color_name": "<short English name, 1-2 words, evocative — e.g. Warm Ivory, Soft Sand, Deep Graphite. If input color_name exists, use or refine it.>",
  "color_hex": "<hex code matching the color name, e.g. #EDE3D2 for warm ivory>",
  "product_description": "<2 elegant sentences about the material and visual effect (English, premium tone)>",
  "design_intent": "<one short poetic line about the surface or space, max 12 words, English>"
}

Style examples:
- product_description: "Travertino Imperium is a hand-applied lime plaster that reveals the depth and movement of natural stone. Each surface develops a quiet, breathing patina that softens light and adds tactile presence to the space."
- design_intent: "Surfaces that hold light, depth, and quiet luxury."

OUTPUT ONLY JSON."""


async def generate_copy(intent: dict) -> dict:
    system = SYSTEMS.get(intent.get("system"))
    if not system:
        return {}

    spec = {
        "product_title": system["display_name"],
        "chemistry": system.get("chemistry", ""),
        "tool": system.get("tool", ""),
        "zone": intent.get("zone", "Interior"),
        "color_type": intent.get("color_type", "light"),
        "color_name": intent.get("color_name"),
    }
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=COPY_PROMPT,
        messages=[{"role": "user", "content": json.dumps(spec, ensure_ascii=False)}],
    )
    raw = response.content[0].text
    try:
        return _extract_json(raw)
    except Exception:
        return {}


# ─────────────────────────────────────────────────────────────
# VOICE TRANSCRIPTION (без изменений)
# ─────────────────────────────────────────────────────────────

async def transcribe_voice(audio_path: str) -> str:
    import asyncio
    import tempfile
    import speech_recognition as sr
    from pydub import AudioSegment

    audio = AudioSegment.from_file(audio_path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
    audio.export(wav_path, format="wav")

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)

    try:
        os.unlink(wav_path)
    except OSError:
        pass

    loop = asyncio.get_event_loop()

    def _recognize():
        for lang in ("ru-RU", "en-US", "th-TH"):
            try:
                return r.recognize_google(audio_data, language=lang)
            except sr.UnknownValueError:
                continue
        raise sr.UnknownValueError()

    try:
        return await loop.run_in_executor(None, _recognize)
    except sr.UnknownValueError:
        raise ValueError("Could not recognise speech — please try again or type your request.")
    except sr.RequestError as e:
        raise ValueError(f"Speech recognition service error: {e}")
