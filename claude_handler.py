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

PARSE_PROMPT = f"""You extract a structured intent from a Pratta Thailand employee's request describing what a client wants. Output STRICT JSON only. No math, no calculations.

STEP 1 — DECIDE THE REQUEST TYPE (`mode`):

- "standard" — a decorative coating / paint SYSTEM quoted by area in m². Signals: a known catalog system name + an area in m², prices NOT dictated by the employee (we compute from the price list).
- "custom" — anything that is NOT a per-m² system quote. Signals: large samples / sample boards ("большой образец", "sample board"), panels, furniture, decor pieces, one-off products or services, and especially when the employee DICTATES the prices themselves ("два образца по 5000 бат", "панно за 15к", "3 ชิ้น ชิ้นละ 4000").
- If the employee names a catalog system AND an area in m² AND does not dictate per-item prices → "standard". If they list items with their own prices → "custom". When genuinely ambiguous, prefer "custom" only if explicit per-item prices are present; otherwise "standard".

IF mode = "custom", OUTPUT THIS SCHEMA INSTEAD OF THE STANDARD ONE:

{{
  "mode": "custom",
  "title": "<short elegant English title for the proposal subject, e.g. 'Travertino Sample Boards', 'Decorative Panel — Marmorino'>",
  "client_name": "<string or null>",
  "items": [
    {{"name": "<item name in English>", "quantity": <number>, "unit": "<pcs / set / m² / lm / hour>", "unit_price": <THB number or null if NOT stated by the employee>}}
  ],
  "notes": "<important conditions mentioned by the employee (delivery, deadline, etc.) or null>"
}}

Custom rules:
- Prices come ONLY from the employee's words. NEVER invent or estimate a price — use null if not stated.
- Shorthand: "5к" / "5k" / "5 тыс" → 5000; "15к" / "15k" → 15000.
- Item names in English (the team is international) — translate from Russian / Thai.
- quantity defaults to 1 if not stated. unit defaults to "pcs".
- Do NOT multiply or sum anything — just extract.

IF mode = "standard", use the schema below and add "mode": "standard" to the output.

ALLOWED `system` values (use the exact id):
{_SYSTEM_LIST_TEXT}

Notes on mapping common names (be tolerant to typos / speech-to-text distortions):
- "travertino" / "travertin" / "травертин" / "имерум" / "imperium" / "ทราเวอร์ทิโน" / "ทราเวอติโน" → travertino_imperium
- "venetian" / "venetsian" / "венецианка" / "антико" / "เวเนเชียน" / "อันติโก เวเนเซียโน" → antico_veneziano
- "marmorino" / "мармарин" / "carrara" / "кеара" / "มาร์โมริโน" / "คาร์รารา" → marmorino_carrara (unless explicitly Antico Veneziano)
- "silk line" / "ซิลค์ ไลน์" — pick the specific product the user named (seta_exclusive, antico_velluto, etc.)
- "marmorino floor mono" / "floor mono" / "microcement" / "ไมโครซีเมนต์" / "พื้นไมโครซีเมนต์" → marmorino_floor_mono
- "metalline gold" / "เมทัลไลน์ โกลด์" / "ทอง" → metalline_gold_system
- "metalline silver" / "เมทัลไลน์ ซิลเวอร์" / "เงิน" → metalline_silver_system
- "metalline bronze" / "เมทัลไลน์ บรอนซ์" / "ทองแดง" → metalline_bronze_system
- PAINTS — be especially tolerant to STT distortions:
    "plastogum" / "пластогум" / "пластагум" / "ластагам" / "lastagam" / "plastagum" / "пластик" / "эластомер" / "พลาสโตกัม"
    → plastogum
    "mister quartz" / "mr quartz" / "quartz" / "мистер кварц" / "кварц" / "кварцевая" / "квартц" / "куартц" / "лотос" / "lotus" / "มิสเตอร์ ควอตซ์" / "ควอตซ์"
    → mister_quartz (hero for wet zones, facades, lotus effect)
    A bare "краска" / "paint" / "สี" with no other product name → plastogum (our hero paint)
    "theia" / "тея" / "тэя" / "egshell" / "เธีย" / "อีกเชลล์" → theia
    "int est" / "int&est" / "интест" / "อินท์ แอนด์ เอสท์" → int_est
- If the request mentions BOTH a plaster system AND a paint ("manu + плюс плагостум на потолок") — pick the PRIMARY product (the one with more m² or mentioned first). The bot handles one system per KP.
- If the input is clearly a paint name even slightly distorted — map to the closest paint system. Do NOT return null.

OUTPUT JSON SCHEMA — every field required (use null where unknown):

{{
  "mode": "standard",
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
- INPUT MAY BE IN ENGLISH, RUSSIAN OR THAI. Be tolerant to mixed-language messages.
- If user says "светлый/light/light tone/อ่อน/สีอ่อน" → color_type: "light"
- If user says "тёмный/dark/глубокий/เข้ม/สีเข้ม/ดาร์ค" → color_type: "dark"
- Zone mapping:
    * "interior/интерьер/ภายใน/ห้อง/ในบ้าน" → "Interior"
    * "exterior/exterior/фасад/экстерьер/ภายนอก/ฟาซาด/นอกบ้าน" → "Exterior"
    * "wet zone/мокрая/мокрая зона/โซนเปียก/ห้องน้ำ/พื้นที่เปียก" → "Wet zone"
- Area mapping: "квадратных метров/sq m/sqm/m²/ตารางเมตร/ตร.ม./ตรม" → number in m².
- Default zone: "Interior"
- Default color_type: "light"
- Default application_included:
    * For PAINTS (plastogum, mister_quartz, int_est, theia) → DEFAULT FALSE. Only set true if user EXPLICITLY says "с нанесением/with works/under turnkey/под ключ/airless/พร้อมติดตั้ง/ติดตั้งด้วย".
    * For all other systems (plasters, brush, sponge, floor) → default TRUE if unclear; false only if user says "только материал/only material/самонанесение/เฉพาะวัสดุ/ไม่ติดตั้ง".
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

REFINE_PROMPT = """You take a previous intent JSON and a refinement message from the employee. Return a NEW intent JSON with the changes applied. Keep all unchanged fields the same (including "mode"). Output JSON only.

Possible refinements for mode "standard":
- "увеличь до X м²" / "make it X sqm" → update area
- "замени финиш на silver" / "use silver" → update finish to metalline_silver
- "пусть будет тёмный" / "switch to dark" → color_type: dark
- "без нанесения" / "material only" → application_included: false
- "имя клиента Ivan Petrov" → client_name
- "добавь зону мокрая" → zone: "Wet zone"

Possible refinements for mode "custom":
- "поменяй цену на X" / "make it X baht" → update unit_price of the matching item (never invent prices)
- "добавь ещё доставку 2000" → append a new item
- "убери второй пункт" / "remove the panel" → delete the matching item
- "сделай 3 штуки" → update quantity
- "имя клиента ..." → client_name
- Shorthand: "5к"/"5k" → 5000

Only switch mode if the employee clearly asks for the other type of proposal.

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


CUSTOM_COPY_PROMPT = """You write elegant English marketing copy for a Pratta Thailand bespoke commercial proposal PDF (custom items: large samples, sample boards, panels, decor pieces, non-standard works). Premium tone, restrained luxury — short, evocative, never salesy.

You receive a spec with: title, items (list of names), notes. Return JSON only:

{
  "product_description": "<2 elegant sentences about these bespoke pieces — hand-crafted by Pratta masters with authentic Italian materials (English, premium tone)>",
  "design_intent": "<one short poetic line, max 12 words, English>"
}

OUTPUT ONLY JSON."""


async def generate_copy(intent: dict) -> dict:
    if intent.get("mode") == "custom":
        spec = {
            "title": intent.get("title"),
            "items": [it.get("name") for it in (intent.get("items") or [])],
            "notes": intent.get("notes"),
        }
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=CUSTOM_COPY_PROMPT,
            messages=[{"role": "user", "content": json.dumps(spec, ensure_ascii=False)}],
        )
        try:
            return _extract_json(response.content[0].text)
        except Exception:
            return {}

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
