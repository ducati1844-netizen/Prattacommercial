from __future__ import annotations

import base64
import mimetypes
import os
import tempfile

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def _thb(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(value)


def _photo_to_data_uri(path: str) -> str | None:
    """Прочитать файл и вернуть data: URI для встраивания в HTML."""
    if not path or not os.path.exists(path):
        return None
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def generate_kp_pdf(kp_data: dict) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["thb"] = _thb

    # подготовим фото — переведём пути в data URI
    photos_raw = kp_data.get("photos") or []
    photo_uris = []
    for p in photos_raw:
        uri = _photo_to_data_uri(p)
        if uri:
            photo_uris.append(uri)
    kp_data = {**kp_data, "photo_uris": photo_uris}

    template = env.get_template("kp.html")
    html_content = template.render(**kp_data)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    HTML(string=html_content, base_url=template_dir).write_pdf(pdf_path)
    return pdf_path
