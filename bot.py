from __future__ import annotations

import asyncio
import logging
import os
import tempfile

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

from calculator import compute_kp, compute_custom_kp
from claude_handler import (
    parse_intent,
    refine_intent,
    generate_copy,
    transcribe_voice,
)
from pdf_generator import generate_kp_pdf
from i18n import T

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WAITING, CONFIRMING, REFINING = range(3)
MAX_PHOTOS = 6


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _fmt(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def _summary(kp: dict, intent: dict, photos_count: int) -> str:
    if kp.get("is_custom"):
        return _summary_custom(kp, intent, photos_count)
    lines = [
        T("summary_product", title=kp["product_title"]),
        T("summary_area", area=kp["area"], zone=kp["zone"]),
        T("summary_color", color_name=kp["color_name"], tone=intent.get("color_type", "light")),
    ]
    if intent.get("finish"):
        lines.append(T("summary_finish", finish=intent["finish"]))
    if intent.get("client_name"):
        lines.append(T("summary_client", client=intent["client_name"]))

    lines += ["", T("summary_materials", value=_fmt(kp["materials_total"]))]
    if kp.get("colorant_total"):
        lines.append(T("summary_colorant", value=_fmt(kp["colorant_total"])))
    if kp.get("works_total"):
        lines.append(T("summary_works", value=_fmt(kp["works_total"])))
    lines += [
        "",
        T("summary_total", value=_fmt(kp["total"])),
        T("summary_per_sqm", value=_fmt(kp["price_per_sqm"])),
    ]
    if photos_count:
        lines.append(T("summary_photos", n=photos_count))

    lines.append(T("summary_hint"))
    return "\n".join(lines)


def _summary_custom(kp: dict, intent: dict, photos_count: int) -> str:
    lines = [T("summary_custom_header"), T("summary_product", title=kp["product_title"])]
    if intent.get("client_name"):
        lines.append(T("summary_client", client=intent["client_name"]))
    lines.append("")
    for group in kp["materials"]:
        for item in group["items"]:
            lines.append(T(
                "summary_custom_item",
                name=item["name"],
                qty=item["quantity"],
                unit=item["package"],
                price=_fmt(item["unit_price"]),
                total=_fmt(item["total"]),
            ))
    if kp.get("notes"):
        lines += ["", T("summary_custom_notes", notes=kp["notes"])]
    lines += ["", T("summary_total", value=_fmt(kp["total"]))]
    if photos_count:
        lines.append(T("summary_photos", n=photos_count))
    lines.append(T("summary_custom_hint"))
    return "\n".join(lines)


def _confirm_keyboard(photos_count: int):
    photo_label = T("btn_add_photo_count", n=photos_count) if photos_count else T("btn_add_photo")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T("btn_generate"), callback_data="generate")],
        [InlineKeyboardButton(T("btn_refine"), callback_data="refine"),
         InlineKeyboardButton(photo_label, callback_data="add_photo")],
        [InlineKeyboardButton(T("btn_clear_photos"), callback_data="clear_photos")],
    ])


def _ensure_state(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("photos", [])
    context.user_data.setdefault("intent", None)
    context.user_data.setdefault("kp_data", None)
    context.user_data.setdefault("history", [])


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
    await update.message.reply_text(T("welcome"), parse_mode="Markdown")
    return WAITING


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cleanup_photos(context)
    context.user_data.clear()
    _ensure_state(context)
    await update.message.reply_text(T("reset_done"))
    return WAITING


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    text = update.message.text
    context.user_data["history"].append(("user", text))
    return await _process_request(update, context, text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    msg = await update.message.reply_text(T("voice_recognizing"))

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        ogg_path = tmp.name
    await file.download_to_drive(ogg_path)

    try:
        transcription = await transcribe_voice(ogg_path)
        await msg.edit_text(T("voice_recognized", text=transcription), parse_mode="Markdown")
        context.user_data["history"].append(("voice", transcription))
        return await _process_request(update, context, transcription)
    except Exception as e:
        await msg.edit_text(T("voice_error", err=str(e)))
        return WAITING
    finally:
        if os.path.exists(ogg_path):
            os.unlink(ogg_path)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    photos = context.user_data["photos"]
    if len(photos) >= MAX_PHOTOS:
        await update.message.reply_text(T("photo_max", max=MAX_PHOTOS))
        return None

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        photo_path = tmp.name
    await file.download_to_drive(photo_path)
    photos.append(photo_path)

    kp_data = context.user_data.get("kp_data")
    if kp_data:
        intent = context.user_data["intent"]
        await update.message.reply_text(
            f"{T('photo_added', n=len(photos), max=MAX_PHOTOS)}\n\n{_summary(kp_data, intent, len(photos))}",
            reply_markup=_confirm_keyboard(len(photos)),
            parse_mode="Markdown",
        )
        return CONFIRMING

    await update.message.reply_text(T("photo_received_no_kp", n=len(photos), max=MAX_PHOTOS))
    return None


async def _process_request(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    processing = await update.message.reply_text(T("computing"))
    try:
        intent = await parse_intent(user_input)
        await _finalize(update, context, intent, processing)
        return CONFIRMING
    except Exception as e:
        await processing.edit_text(T("parse_error", err=str(e)))
        return WAITING


async def _finalize(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    intent: dict, processing_msg):
    copy_task = asyncio.create_task(generate_copy(intent))
    if intent.get("mode") == "custom":
        kp = compute_custom_kp(intent)
    else:
        kp = compute_kp(intent)
    try:
        copy = await copy_task
    except Exception:
        copy = {}
    if copy:
        kp["product_description"] = copy.get("product_description", kp["product_description"])
        kp["design_intent"] = copy.get("design_intent", kp["design_intent"])
        if not kp.get("is_custom"):
            if copy.get("color_name"):
                kp["color_name"] = copy["color_name"]
            if copy.get("color_hex"):
                kp["color_hex"] = copy["color_hex"]

    context.user_data["intent"] = intent
    context.user_data["kp_data"] = kp
    photos_count = len(context.user_data.get("photos", []))

    await processing_msg.delete()
    await update.message.reply_text(
        f"{T('kp_ready_header')}\n\n{_summary(kp, intent, photos_count)}",
        reply_markup=_confirm_keyboard(photos_count),
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    query = update.callback_query
    await query.answer()

    if query.data == "generate":
        await _generate_pdf(update, context)
        return WAITING

    if query.data == "refine":
        await query.edit_message_text(T("refine_prompt"), parse_mode="Markdown")
        return REFINING

    if query.data == "add_photo":
        photos = context.user_data.get("photos", [])
        await query.edit_message_text(T("add_photo_prompt", n=len(photos), max=MAX_PHOTOS))
        return CONFIRMING

    if query.data == "clear_photos":
        _cleanup_photos(context)
        kp = context.user_data.get("kp_data")
        intent = context.user_data.get("intent")
        if kp and intent:
            await query.edit_message_text(
                T("photos_cleared_with_summary", summary=_summary(kp, intent, 0)),
                reply_markup=_confirm_keyboard(0),
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(T("photos_cleared"))
        return CONFIRMING

    return CONFIRMING


async def _generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = (query.message.chat_id if query else update.effective_chat.id)
    if query:
        await query.edit_message_text(T("generating_pdf"))
    else:
        await context.bot.send_message(chat_id=chat_id, text=T("generating_pdf"))

    kp_data = context.user_data.get("kp_data") or {}
    kp_data = {**kp_data, "photos": context.user_data.get("photos", [])}

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
                caption=T("pdf_caption"),
            )

        try:
            os.unlink(pdf_path)
        except OSError:
            pass

        await context.bot.send_message(chat_id=chat_id, text=T("next_kp_prompt"))
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=T("pdf_error", err=str(e)))


async def handle_refinement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_state(context)
    text = update.message.text
    prev_intent = context.user_data.get("intent")
    if not prev_intent:
        return await _process_request(update, context, text)

    context.user_data["history"].append(("refine", text))
    processing = await update.message.reply_text(T("refine_computing"))
    try:
        new_intent = await refine_intent(prev_intent, text)
        await _finalize(update, context, new_intent, processing)
        return CONFIRMING
    except Exception as e:
        await processing.edit_text(T("refine_error", err=str(e)))
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
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("reset", cmd_reset),
        ],
    )

    app.add_handler(conv)
    logger.info("Bot started (BOT_LANG=%s). Press Ctrl+C to stop.", os.getenv("BOT_LANG", "en"))
    app.run_polling()


if __name__ == "__main__":
    main()
