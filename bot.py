from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from calculator import compute_kp
from claude_handler import (
    parse_intent,
    refine_intent,
    generate_copy,
    transcribe_voice,
)
from pdf_generator import generate_kp_pdf

load_dotenv()

logger = logging.getLogger(__name__)

WAITING, CONFIRMING, REFINING, AWAITING_DEAL_ID = range(4)
MAX_PHOTOS = 6

BITRIX_WEBHOOK_URL = os.getenv(
    "BITRIX_WEBHOOK_URL",
    "https://pratta.bitrix24.ru/rest/1/13bvcl4q30kjmrop",
).rstrip("/")
KP_ATTACH_QUEUE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "kp_attach_queue.json"
)


# ─────────────────────────────────────────────────────────────
# BITRIX ATTACH
# ─────────────────────────────────────────────────────────────

def _build_comment(kp_data: dict) -> str:
    product = kp_data.get("product_title", "?")
    area = kp_data.get("area", "?")
    total = kp_data.get("total", "?")
    try:
        total_fmt = f"{int(total):,}".replace(",", " ")
    except (TypeError, ValueError):
        total_fmt = str(total)
    client = kp_data.get("client_name") or kp_data.get("intent", {}).get("client_name") if isinstance(kp_data.get("intent"), dict) else kp_data.get("client_name")
    lines = [
        "📎 КП отправлен клиенту через @Commercialprattabot",
        f"Продукт: {product}",
        f"Площадь: {area} м²",
        f"Сумма: {total_fmt} THB",
    ]
    if client:
        lines.append(f"Клиент: {client}")
    return "\n".join(lines)


def _enqueue_failed_attach(deal_id: int, pdf_path: str, kp_data: dict, error: str) -> None:
    """Persist failed attach for later manual/automated retry."""
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "deal_id": deal_id,
        "pdf_path": pdf_path,
        "product_title": kp_data.get("product_title"),
        "area": kp_data.get("area"),
        "total": kp_data.get("total"),
        "client_name": kp_data.get("client_name"),
        "error": error,
    }
    try:
        queue = []
        if os.path.exists(KP_ATTACH_QUEUE_PATH):
            with open(KP_ATTACH_QUEUE_PATH, "r", encoding="utf-8") as f:
                queue = json.load(f)
        queue.append(entry)
        with open(KP_ATTACH_QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        logger.warning("Enqueued failed Bitrix attach for deal %s -> %s", deal_id, KP_ATTACH_QUEUE_PATH)
    except Exception as e:
        logger.error("Failed to write retry queue: %s", e)


def attach_to_bitrix_deal(deal_id: int, pdf_path: str, kp_data: dict) -> bool:
    """
    Attach PDF to a Bitrix deal timeline via crm.timeline.comment.add (FILES[] base64).
    Retries 3 times with exponential backoff (1s, 2s, 4s). On final failure, enqueues
    to local retry queue and returns False.
    """
    if not deal_id:
        return False
    if not os.path.exists(pdf_path):
        logger.error("Bitrix attach: PDF not found: %s", pdf_path)
        return False

    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("ascii")
    filename = os.path.basename(pdf_path)

    payload = {
        "fields": {
            "ENTITY_ID": int(deal_id),
            "ENTITY_TYPE": "deal",
            "COMMENT": _build_comment(kp_data),
            "FILES": [[filename, pdf_b64]],
        }
    }
    url = f"{BITRIX_WEBHOOK_URL}/crm.timeline.comment.add.json"

    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=60)
            data = r.json() if r.content else {}
            if r.ok and data.get("result"):
                logger.info("Bitrix attach OK deal=%s comment_id=%s", deal_id, data.get("result"))
                return True
            last_err = f"HTTP {r.status_code} body={str(data)[:300]}"
            logger.warning("Bitrix attach attempt %s failed: %s", attempt + 1, last_err)
        except Exception as e:
            last_err = repr(e)
            logger.warning("Bitrix attach attempt %s raised: %s", attempt + 1, last_err)
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s

    _enqueue_failed_attach(deal_id, pdf_path, kp_data, last_err or "unknown")
    return False

WELCOME = (
    "👋 *Pratta — генератор КП*\n\n"
    "Опишите задачу — текстом или голосом:\n"
    "• Продукт / система\n"
    "• Площадь (м²)\n"
    "• Зона: интерьер / экстерьер / мокрая\n"
    "• Цвет: светлый / тёмный (можно конкретное имя)\n"
    "• Нанесение под ключ или только материал?\n"
    "• Имя клиента (по желанию)\n\n"
    "_Пример: «Клиент Иван — Travertino Imperium, гостиная 150 м², светлый, под ключ»_\n\n"
    "📷 Можно прислать фото объекта / референсы — попадут отдельной страницей в PDF.\n"
    "/reset — начать заново."
)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _summary(kp: dict, intent: dict, photos_count: int) -> str:
    lines = [
        f"📦 *{kp['product_title']}*",
        f"📐 Площадь: {kp['area']} м²  ·  {kp['zone']}",
        f"🎨 Цвет: {kp['color_name']} ({intent.get('color_type', 'light')})",
    ]
    if intent.get("finish"):
        lines.append(f"✨ Финиш: {intent['finish']}")
    if intent.get("client_name"):
        lines.append(f"👤 Клиент: {intent['client_name']}")

    lines += ["", f"💰 Материалы: *{kp['materials_total']:,} THB*".replace(",", " ")]
    if kp.get("colorant_total"):
        lines.append(f"   _в т.ч. колеровка: {kp['colorant_total']:,} THB_".replace(",", " "))
    if kp.get("works_total"):
        lines.append(f"🔨 Нанесение: *{kp['works_total']:,} THB*".replace(",", " "))
    lines += [
        "",
        f"*ИТОГО: {kp['total']:,} THB*".replace(",", " "),
        f"Цена за м²: {kp['price_per_sqm']:,} THB/м²".replace(",", " "),
    ]
    if photos_count:
        lines.append(f"\n📷 Фото: {photos_count} шт.")

    # подсказка для правок
    lines.append("\n_✏️ Можно изменить: цвет, площадь, финиш, без нанесения, имя клиента…_")
    return "\n".join(lines)


def _confirm_keyboard(photos_count: int):
    photo_label = f"📷 Фото ({photos_count})" if photos_count else "📷 Добавить фото"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Сгенерировать PDF", callback_data="generate")],
        [InlineKeyboardButton("✏️ Изменить расчёт", callback_data="refine"),
         InlineKeyboardButton(photo_label, callback_data="add_photo")],
        [InlineKeyboardButton("🗑 Очистить фото", callback_data="clear_photos")],
    ])


def _ensure_state(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("photos", [])
    context.user_data.setdefault("intent", None)
    context.user_data.setdefault("kp_data", None)
    context.user_data.setdefault("history", [])  # для контекста правок
    context.user_data.setdefault("bitrix_deal_id", None)


def _cleanup_photos(context: ContextTypes.DEFAULT_TYPE):
    for path in context.user_data.get("photos", []):
        try:
            if os.path.exists(path):
                os.unlink(path)
        except OSError:
            pass
    context.user_data["photos"] = []


# ─────────────────────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    await update.message.reply_text(WELCOME, parse_mode="Markdown")
    return WAITING


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cleanup_photos(context)
    context.user_data.clear()
    _ensure_state(context)
    await update.message.reply_text("Очищено. Опишите новый проект.")
    return WAITING


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    text = update.message.text
    context.user_data["history"].append(("user", text))
    return await _process_request(update, context, text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    msg = await update.message.reply_text("🎤 Распознаю голос...")

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        ogg_path = tmp.name
    await file.download_to_drive(ogg_path)

    try:
        transcription = await transcribe_voice(ogg_path)
        await msg.edit_text(f"📝 _Распознал:_\n_{transcription}_", parse_mode="Markdown")
        context.user_data["history"].append(("voice", transcription))
        return await _process_request(update, context, transcription)
    except Exception as e:
        await msg.edit_text(f"❌ Не удалось распознать: {e}\n\nПопробуйте ещё раз или напишите текстом.")
        return WAITING
    finally:
        if os.path.exists(ogg_path):
            os.unlink(ogg_path)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фото можно присылать на любом этапе — копятся, прикрепляются к PDF."""
    _ensure_state(context)
    photos = context.user_data["photos"]
    if len(photos) >= MAX_PHOTOS:
        await update.message.reply_text(
            f"📷 Уже {MAX_PHOTOS} фото — максимум. "
            "Нажмите «🗑 Очистить фото» если нужно начать заново."
        )
        return None

    photo = update.message.photo[-1]  # самое крупное разрешение
    file = await context.bot.get_file(photo.file_id)
    suffix = ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        photo_path = tmp.name
    await file.download_to_drive(photo_path)
    photos.append(photo_path)

    kp_data = context.user_data.get("kp_data")
    if kp_data:
        # КП уже посчитано — показать обновлённую сводку с фото
        intent = context.user_data["intent"]
        await update.message.reply_text(
            f"📷 Фото добавлено ({len(photos)}/{MAX_PHOTOS}).\n\n{_summary(kp_data, intent, len(photos))}",
            reply_markup=_confirm_keyboard(len(photos)),
            parse_mode="Markdown",
        )
        return CONFIRMING

    await update.message.reply_text(
        f"📷 Фото принято ({len(photos)}/{MAX_PHOTOS}). Опишите проект, чтобы посчитать КП."
    )
    return None  # не меняем стадию


async def _process_request(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    processing = await update.message.reply_text("⏳ Считаю КП...")

    try:
        intent = await parse_intent(user_input)
        await _finalize(update, context, intent, processing)
        return CONFIRMING
    except Exception as e:
        await processing.edit_text(
            f"❌ Не получилось разобрать запрос: {e}\n\n"
            "Уточните: продукт, площадь, зона, цвет (светлый/тёмный)."
        )
        return WAITING


async def _finalize(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    intent: dict, processing_msg):
    """Расчёт + копирайт + показ сводки."""
    # креатив + расчёт параллельно — copy не блокирует расчёт
    copy_task = asyncio.create_task(generate_copy(intent))
    kp = compute_kp(intent)
    try:
        copy = await copy_task
    except Exception:
        copy = {}
    if copy:
        kp["product_description"] = copy.get("product_description", kp["product_description"])
        kp["design_intent"] = copy.get("design_intent", kp["design_intent"])
        if copy.get("color_name"):
            kp["color_name"] = copy["color_name"]
        if copy.get("color_hex"):
            kp["color_hex"] = copy["color_hex"]

    context.user_data["intent"] = intent
    context.user_data["kp_data"] = kp
    photos_count = len(context.user_data.get("photos", []))

    await processing_msg.delete()
    await update.message.reply_text(
        f"*КП готово:*\n\n{_summary(kp, intent, photos_count)}",
        reply_markup=_confirm_keyboard(photos_count),
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    query = update.callback_query
    await query.answer()

    if query.data == "generate":
        # Если deal_id ещё не задан в этой сессии — спрашиваем перед генерацией
        if context.user_data.get("bitrix_deal_id") is None:
            await query.edit_message_text(
                "🆔 *Bitrix Deal ID?*\n\n"
                "Скопируйте номер сделки из URL Bitrix (например, 1359) и пришлите числом.\n"
                "Введите `-1` или `skip`, если не хотите прикреплять КП к сделке.",
                parse_mode="Markdown",
            )
            return AWAITING_DEAL_ID
        await _generate_pdf(update, context)
        return WAITING

    if query.data == "refine":
        await query.edit_message_text(
            "✏️ Что меняем? Опишите правку одной фразой.\n\n"
            "_Примеры:_\n"
            "• _«увеличь до 200 м²»_\n"
            "• _«пусть будет тёмный»_\n"
            "• _«замени финиш на silver»_\n"
            "• _«без нанесения»_\n"
            "• _«клиент Кирилл»_",
            parse_mode="Markdown",
        )
        return REFINING

    if query.data == "add_photo":
        photos = context.user_data.get("photos", [])
        await query.edit_message_text(
            f"📷 Пришлите фото проекта (объект, референс, образец).\n"
            f"Уже добавлено: {len(photos)}/{MAX_PHOTOS}.\n\n"
            "Когда закончите — снова опишите КП или нажмите кнопку повторного расчёта.",
        )
        return CONFIRMING

    if query.data == "clear_photos":
        _cleanup_photos(context)
        kp = context.user_data.get("kp_data")
        intent = context.user_data.get("intent")
        if kp and intent:
            await query.edit_message_text(
                f"🗑 Фото очищены.\n\n{_summary(kp, intent, 0)}",
                reply_markup=_confirm_keyboard(0),
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text("🗑 Фото очищены.")
        return CONFIRMING

    return CONFIRMING


async def _generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = (query.message.chat_id if query else update.effective_chat.id)
    if query:
        await query.edit_message_text("⏳ Генерирую PDF...")
    else:
        await context.bot.send_message(chat_id=chat_id, text="⏳ Генерирую PDF...")

    kp_data = context.user_data.get("kp_data") or {}
    kp_data = {**kp_data, "photos": context.user_data.get("photos", [])}
    deal_id = context.user_data.get("bitrix_deal_id")

    pdf_path = None
    try:
        pdf_path = generate_kp_pdf(kp_data)
        client = kp_data.get("client_name") or "Project"
        safe_client = "".join(c if c.isalnum() else "_" for c in client)[:30]
        filename = f"KP_Pratta_{kp_data.get('product_title', 'Quote').replace(' ', '_')}_{safe_client}.pdf"

        with open(pdf_path, "rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=f,
                filename=filename,
                caption="✅ КП готово. Отправьте клиенту.",
            )

        # Attach to Bitrix deal timeline (best-effort, Telegram already delivered).
        if deal_id and deal_id != -1:
            try:
                ok = await asyncio.to_thread(
                    attach_to_bitrix_deal, deal_id, pdf_path, kp_data
                )
                if ok:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"📎 PDF прикреплён к сделке Bitrix #{deal_id}.",
                    )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚠️ Не удалось прикрепить PDF к сделке #{deal_id} "
                            "после 3 попыток. Запись добавлена в очередь retry."
                        ),
                    )
            except Exception as e:
                logger.error("attach_to_bitrix_deal raised: %s", e)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ Bitrix attach error: {e}",
                )

        try:
            os.unlink(pdf_path)
        except OSError:
            pass

        await context.bot.send_message(
            chat_id=chat_id,
            text="Создать ещё одно КП? Опишите следующий проект или /reset.",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Ошибка генерации PDF: {e}",
        )


async def handle_deal_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает Bitrix Deal ID, затем запускает генерацию PDF."""
    _ensure_state(context)
    text = (update.message.text or "").strip()
    if text.lower() in ("-1", "skip", "пропустить", "нет", "no"):
        context.user_data["bitrix_deal_id"] = -1
        await update.message.reply_text("⏭ Пропускаю Bitrix. Генерирую PDF только в Telegram...")
    else:
        try:
            deal_id = int(text)
            if deal_id <= 0:
                raise ValueError
            context.user_data["bitrix_deal_id"] = deal_id
            await update.message.reply_text(f"✅ Deal #{deal_id} зафиксирован. Генерирую PDF...")
        except ValueError:
            await update.message.reply_text(
                "Не похоже на число. Пришлите целый Deal ID (например, 1359) "
                "или `-1` чтобы пропустить.",
                parse_mode="Markdown",
            )
            return AWAITING_DEAL_ID

    await _generate_pdf(update, context)
    return WAITING


async def handle_refinement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    text = update.message.text
    prev_intent = context.user_data.get("intent")
    if not prev_intent:
        return await _process_request(update, context, text)

    context.user_data["history"].append(("refine", text))
    processing = await update.message.reply_text("⏳ Пересчитываю...")
    try:
        new_intent = await refine_intent(prev_intent, text)
        await _finalize(update, context, new_intent, processing)
        return CONFIRMING
    except Exception as e:
        await processing.edit_text(f"❌ Не получилось применить правку: {e}")
        return CONFIRMING


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        per_message=False,
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("kp", cmd_start),
            CommandHandler("reset", cmd_reset),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            MessageHandler(filters.VOICE, handle_voice),
            MessageHandler(filters.PHOTO, handle_photo),
        ],
        states={
            WAITING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
                MessageHandler(filters.VOICE, handle_voice),
                MessageHandler(filters.PHOTO, handle_photo),
            ],
            CONFIRMING: [
                CallbackQueryHandler(handle_callback),
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_refinement),
                MessageHandler(filters.VOICE, handle_voice),
            ],
            REFINING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_refinement),
                MessageHandler(filters.VOICE, handle_voice),
                MessageHandler(filters.PHOTO, handle_photo),
            ],
            AWAITING_DEAL_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deal_id),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("reset", cmd_reset),
        ],
    )

    app.add_handler(conv)
    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
