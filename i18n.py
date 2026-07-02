"""
Bilingual UI strings for the Pratta KP bot.
Language selected via env BOT_LANG = "en" (default) or "th".
The PDF output is always English regardless of BOT_LANG — only the
Telegram chat interface localizes.
"""
from __future__ import annotations

import os

BOT_LANG = os.getenv("BOT_LANG", "en").lower().strip()
if BOT_LANG not in ("en", "th"):
    BOT_LANG = "en"


STRINGS = {
    "en": {
        "welcome": (
            "👋 *Pratta — Commercial Proposal Generator*\n\n"
            "Describe the project in text or voice:\n"
            "• Product / system\n"
            "• Area (m²)\n"
            "• Zone: interior / exterior / wet zone\n"
            "• Colour: light / dark (optional name)\n"
            "• Turnkey application or material only?\n"
            "• Client name (optional)\n\n"
            "_Example: \"Client Ivan — Travertino Imperium, living room 150 m², light tone, turnkey\"_\n\n"
            "🛠 *Custom items too* — just say what and at what price:\n"
            "_\"Two large Travertino sample boards, 5 000 baht each, plus delivery 1 500\"_\n\n"
            "📷 You can attach photos of the site / references — they will go on a separate page in the PDF.\n"
            "/reset — start over."
        ),
        "reset_done": "Cleared. Describe the new project.",
        "computing": "⏳ Computing the proposal...",
        "parse_error": "❌ Couldn't parse your request: {err}\n\nPlease specify: product, area, zone, colour (light/dark).",
        "voice_recognizing": "🎤 Transcribing voice...",
        "voice_recognized": "📝 _Transcribed:_\n_{text}_",
        "voice_error": "❌ Voice transcription failed: {err}\n\nTry again or type the request.",
        "photo_added": "📷 Photo added ({n}/{max}).",
        "photo_max": "📷 Already {max} photos — maximum reached. Tap «🗑 Clear photos» to start over.",
        "photo_received_no_kp": "📷 Photo received ({n}/{max}). Describe the project to compute the proposal.",
        "kp_ready_header": "*Proposal ready:*",
        "summary_product": "📦 *{title}*",
        "summary_area": "📐 Area: {area} m²  ·  {zone}",
        "summary_color": "🎨 Colour: {color_name} ({tone})",
        "summary_finish": "✨ Finish: {finish}",
        "summary_client": "👤 Client: {client}",
        "summary_materials": "💰 Materials: *{value} THB*",
        "summary_colorant": "   _incl. tinting: {value} THB_",
        "summary_works": "🔨 Application: *{value} THB*",
        "summary_total": "*TOTAL: {value} THB*",
        "summary_per_sqm": "Price per m²: {value} THB/m²",
        "summary_photos": "\n📷 Photos: {n} pcs.",
        "summary_hint": "\n_✏️ You can change: colour, area, finish, no application, client name…_",
        "summary_custom_header": "🛠 *Bespoke proposal*",
        "summary_custom_item": "• {name} — {qty} {unit} × {price} = *{total} THB*",
        "summary_custom_notes": "📝 _{notes}_",
        "summary_custom_hint": "\n_✏️ You can change: prices, quantities, add or remove items, client name…_",
        "btn_generate": "✅ Generate PDF",
        "btn_refine": "✏️ Modify",
        "btn_add_photo": "📷 Add photo",
        "btn_add_photo_count": "📷 Photos ({n})",
        "btn_clear_photos": "🗑 Clear photos",
        "generating_pdf": "⏳ Generating PDF...",
        "pdf_caption": "✅ Proposal ready. Send to the client.",
        "pdf_error": "❌ PDF generation error: {err}",
        "next_kp_prompt": "Create another proposal? Describe the next project or /reset.",
        "refine_prompt": (
            "✏️ What would you like to change? Describe the edit in one phrase.\n\n"
            "_Examples:_\n"
            "• _\"increase to 200 m²\"_\n"
            "• _\"make it dark\"_\n"
            "• _\"change finish to silver\"_\n"
            "• _\"no application\"_\n"
            "• _\"client Kirill\"_"
        ),
        "add_photo_prompt": (
            "📷 Send a project photo (site, reference, sample).\n"
            "Currently added: {n}/{max}.\n\n"
            "When done — describe the proposal again or tap the recompute button."
        ),
        "photos_cleared": "🗑 Photos cleared.",
        "photos_cleared_with_summary": "🗑 Photos cleared.\n\n{summary}",
        "refine_computing": "⏳ Recomputing...",
        "refine_error": "❌ Couldn't apply the edit: {err}",
    },
    "th": {
        "welcome": (
            "👋 *Pratta — เครื่องมือสร้างใบเสนอราคา*\n\n"
            "อธิบายโครงการเป็นข้อความหรือเสียง:\n"
            "• สินค้า / ระบบ\n"
            "• พื้นที่ (ตร.ม.)\n"
            "• โซน: ภายใน / ภายนอก / โซนเปียก\n"
            "• สี: อ่อน / เข้ม (ใส่ชื่อสีได้)\n"
            "• พร้อมติดตั้งหรือเฉพาะวัสดุ?\n"
            "• ชื่อลูกค้า (ไม่จำเป็น)\n\n"
            "_ตัวอย่าง: \"ลูกค้า Ivan — Travertino Imperium ห้องนั่งเล่น 150 ตร.ม. สีอ่อน พร้อมติดตั้ง\"_\n\n"
            "🛠 *งานสั่งทำก็ได้* — บอกว่าต้องการอะไร ราคาเท่าไหร่:\n"
            "_\"บอร์ดตัวอย่าง Travertino ใหญ่ 2 ชิ้น ชิ้นละ 5,000 บาท พร้อมค่าส่ง 1,500\"_\n\n"
            "📷 ส่งรูปหน้างาน / รูปอ้างอิงได้ — จะถูกใส่ในหน้าแยกของ PDF\n"
            "/reset — เริ่มใหม่"
        ),
        "reset_done": "ล้างข้อมูลแล้ว อธิบายโครงการใหม่ได้เลย",
        "computing": "⏳ กำลังคำนวณใบเสนอราคา...",
        "parse_error": "❌ ไม่สามารถเข้าใจคำขอ: {err}\n\nกรุณาระบุ: สินค้า, พื้นที่, โซน, สี (อ่อน/เข้ม)",
        "voice_recognizing": "🎤 กำลังถอดเสียง...",
        "voice_recognized": "📝 _ถอดเสียงได้:_\n_{text}_",
        "voice_error": "❌ ถอดเสียงไม่สำเร็จ: {err}\n\nลองอีกครั้งหรือพิมพ์ข้อความแทน",
        "photo_added": "📷 เพิ่มรูปแล้ว ({n}/{max})",
        "photo_max": "📷 มี {max} รูปแล้ว — เกินขีดสูงสุด แตะ «🗑 ล้างรูป» เพื่อเริ่มใหม่",
        "photo_received_no_kp": "📷 รับรูปแล้ว ({n}/{max}) อธิบายโครงการเพื่อคำนวณใบเสนอราคา",
        "kp_ready_header": "*ใบเสนอราคาพร้อมแล้ว:*",
        "summary_product": "📦 *{title}*",
        "summary_area": "📐 พื้นที่: {area} ตร.ม.  ·  {zone}",
        "summary_color": "🎨 สี: {color_name} ({tone})",
        "summary_finish": "✨ ฟินิช: {finish}",
        "summary_client": "👤 ลูกค้า: {client}",
        "summary_materials": "💰 วัสดุ: *{value} บาท*",
        "summary_colorant": "   _รวมการผสมสี: {value} บาท_",
        "summary_works": "🔨 ติดตั้ง: *{value} บาท*",
        "summary_total": "*รวม: {value} บาท*",
        "summary_per_sqm": "ราคาต่อ ตร.ม.: {value} บาท/ตร.ม.",
        "summary_photos": "\n📷 รูป: {n} รูป",
        "summary_hint": "\n_✏️ สามารถเปลี่ยน: สี, พื้นที่, ฟินิช, ไม่ติดตั้ง, ชื่อลูกค้า…_",
        "summary_custom_header": "🛠 *ใบเสนอราคางานสั่งทำ*",
        "summary_custom_item": "• {name} — {qty} {unit} × {price} = *{total} บาท*",
        "summary_custom_notes": "📝 _{notes}_",
        "summary_custom_hint": "\n_✏️ สามารถเปลี่ยน: ราคา, จำนวน, เพิ่ม/ลบรายการ, ชื่อลูกค้า…_",
        "btn_generate": "✅ สร้าง PDF",
        "btn_refine": "✏️ แก้ไข",
        "btn_add_photo": "📷 เพิ่มรูป",
        "btn_add_photo_count": "📷 รูป ({n})",
        "btn_clear_photos": "🗑 ล้างรูป",
        "generating_pdf": "⏳ กำลังสร้าง PDF...",
        "pdf_caption": "✅ ใบเสนอราคาพร้อมแล้ว ส่งให้ลูกค้าได้เลย",
        "pdf_error": "❌ ข้อผิดพลาดในการสร้าง PDF: {err}",
        "next_kp_prompt": "สร้างใบเสนอราคาอีกฉบับ? อธิบายโครงการถัดไป หรือ /reset",
        "refine_prompt": (
            "✏️ ต้องการแก้อะไร? อธิบายเป็นประโยคเดียว\n\n"
            "_ตัวอย่าง:_\n"
            "• _\"เพิ่มเป็น 200 ตร.ม.\"_\n"
            "• _\"เปลี่ยนเป็นสีเข้ม\"_\n"
            "• _\"เปลี่ยนฟินิชเป็น silver\"_\n"
            "• _\"ไม่ติดตั้ง\"_\n"
            "• _\"ลูกค้า Kirill\"_"
        ),
        "add_photo_prompt": (
            "📷 ส่งรูปโครงการ (หน้างาน, อ้างอิง, ตัวอย่าง)\n"
            "เพิ่มแล้ว: {n}/{max}\n\n"
            "เมื่อเสร็จ — อธิบายใบเสนอราคาอีกครั้ง หรือกดปุ่มคำนวณซ้ำ"
        ),
        "photos_cleared": "🗑 ล้างรูปแล้ว",
        "photos_cleared_with_summary": "🗑 ล้างรูปแล้ว\n\n{summary}",
        "refine_computing": "⏳ กำลังคำนวณใหม่...",
        "refine_error": "❌ ใช้การแก้ไขไม่สำเร็จ: {err}",
    },
}


def T(key: str, **kwargs) -> str:
    template = STRINGS[BOT_LANG].get(key) or STRINGS["en"].get(key, key)
    return template.format(**kwargs) if kwargs else template
