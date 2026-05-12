from __future__ import annotations

import asyncio
import os
import tempfile

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

WAITING, CONFIRMING, REFINING = range(3)
MAX_PHOTOS = 6

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
    await query.edit_message_text("⏳ Генерирую PDF...")

    kp_data = context.user_data.get("kp_data") or {}
    kp_data = {**kp_data, "photos": context.user_data.get("photos", [])}

    try:
        pdf_path = generate_kp_pdf(kp_data)
        client = kp_data.get("client_name") or "Project"
        safe_client = "".join(c if c.isalnum() else "_" for c in client)[:30]
        filename = f"KP_Pratta_{kp_data.get('product_title', 'Quote').replace(' ', '_')}_{safe_client}.pdf"

        with open(pdf_path, "rb") as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f,
                filename=filename,
                caption="✅ КП готово. Отправьте клиенту.",
            )
        try:
            os.unlink(pdf_path)
        except OSError:
            pass

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Создать ещё одно КП? Опишите следующий проект или /reset.",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ Ошибка генерации PDF: {e}",
        )


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
