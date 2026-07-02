"""
Детерминированный расчёт КП Pratta.
Получает структурированный intent (системы, площадь, цвет, финиш),
возвращает kp_data dict готовый для шаблона.
"""
from __future__ import annotations

import math
from datetime import datetime
from itertools import product as iproduct

from catalog import (
    PRODUCTS,
    SYSTEMS,
    COLORANT,
    resolve_system,
    resolve_finish,
)

WORKING_AREA_FACTOR = 1.10
# Краски считаем без 10% запаса: расход рассчитан точно (выход банки уже за 2 слоя),
# и Свят явно требует «90 м² → 1 банка», без буферного округления вверх.
PAINT_SYSTEM_IDS = {"plastogum", "mister_quartz", "int_est", "theia"}


def _variant_by_tone(family: str, color_type: str) -> str:
    """Привести family + тон → конкретный product_id (P/T для светлых, D/A для тёмных)."""
    suffix = "_pt" if color_type != "dark" else "_da"
    return f"{family}{suffix}"


def _best_pack_combination(needed_m2: float, packs: list[dict]) -> list[dict]:
    """
    Найти самую дешёвую комбинацию пакетов, покрывающую needed_m2.
    Brute-force, ограниченный сверху ceil(needed/min_yield)+1 для каждого пакета.

    Возвращает [{"pack": pack_dict, "qty": int}, ...] (только qty > 0).
    """
    if needed_m2 <= 0:
        return []

    packs_sorted = sorted(packs, key=lambda p: -p["yield_m2"])
    min_yield = min(p["yield_m2"] for p in packs_sorted)
    max_qty_per_pack = int(math.ceil(needed_m2 / min_yield)) + 1
    max_qty_per_pack = min(max_qty_per_pack, 60)  # cap to avoid explosion

    best = None
    ranges = [range(max_qty_per_pack + 1) for _ in packs_sorted]
    for combo in iproduct(*ranges):
        coverage = sum(q * p["yield_m2"] for q, p in zip(combo, packs_sorted))
        if coverage < needed_m2:
            continue
        cost = sum(q * p["price"] for q, p in zip(combo, packs_sorted))
        # Tie-breaker: prefer fewer items
        items_count = sum(combo)
        key = (cost, items_count, -coverage)
        if best is None or key < best["key"]:
            best = {"key": key, "combo": combo}

    if best is None:
        # Fallback: один пакет минимального размера
        smallest = min(packs_sorted, key=lambda p: p["yield_m2"])
        return [{"pack": smallest, "qty": 1}]

    return [
        {"pack": p, "qty": q}
        for p, q in zip(packs_sorted, best["combo"])
        if q > 0
    ]


def _resolve_product_id(layer_product: dict, color_type: str, finish_override: str | None,
                        grade_override: str | None) -> str:
    """Разрешить product id с учётом тона/финиша/градации Intonachino."""
    if layer_product.get("is_finish") and finish_override:
        resolved = resolve_finish(finish_override)
        if resolved:
            return resolved
        return layer_product["id"]
    if layer_product.get("is_grade") and grade_override:
        return grade_override
    if layer_product.get("by_tone"):
        return _variant_by_tone(layer_product["by_tone"], color_type)
    return layer_product["id"]


def _format_color_name(color_type: str, custom_name: str | None) -> tuple[str, str]:
    """Вернуть (display_name, hex). Если custom — приоритет."""
    if custom_name:
        # эвристика: тёплые → ivory, тёмные → graphite
        if color_type == "dark":
            return custom_name, "#3D3A36"
        return custom_name, "#E8DFCF"
    if color_type == "dark":
        return "Deep Graphite", "#3A3633"
    return "Warm Ivory", "#EDE3D2"


def _benefits_for_system(system: dict, zone: str) -> list[str]:
    """3 буллита преимуществ под систему."""
    chem = system.get("chemistry", "")
    benefits: list[str] = []
    if chem == "lime":
        benefits.append("Breathable mineral surface")
    elif chem == "acrylic":
        benefits.append("Durable acrylic coating")
    if system.get("medical_certified"):
        benefits.append("Medical-grade certification")
    if "wet" in (zone or "").lower():
        benefits.append("Water-resistant finish")
    elif "exterior" in (zone or "").lower():
        benefits.append("UV and weather resistant")
    else:
        benefits.append("Luxury tactile finish")
    if len(benefits) < 3:
        benefits.append("Authentic Italian raw materials")
    return benefits[:3]


def compute_kp(intent: dict) -> dict:
    """
    Главная функция. На входе:
      {
        "system": "manu" | "travertino_imperium" | ...,
        "area": float,
        "zone": "Interior" | "Exterior" | "Wet zone",
        "color_type": "light" | "dark",
        "color_name": str | None,
        "finish": str | None,
        "grade": str | None,           # для Intonachino
        "application_included": bool,
        "client_name": str | None,
        "colorant_included": bool,     # включить ли строку колеровки
      }

    На выходе — kp_data, готовый для шаблона.
    """
    system_id = resolve_system(intent.get("system", ""))
    if not system_id:
        raise ValueError(f"Unknown system: {intent.get('system')!r}")
    system = SYSTEMS[system_id]

    area = float(intent.get("area") or 0)
    if area <= 0:
        raise ValueError("Area must be positive")
    area_factor = 1.0 if system_id in PAINT_SYSTEM_IDS else WORKING_AREA_FACTOR
    working_area = area * area_factor

    color_type = (intent.get("color_type") or "light").lower()
    finish_override = intent.get("finish")
    grade_override = intent.get("grade")
    application_included = bool(intent.get("application_included"))
    colorant_included = intent.get("colorant_included")
    if colorant_included is None:
        colorant_included = True  # по умолчанию включать
    client_name = intent.get("client_name")

    # ── собрать слои и материалы ──────────────────────────────
    materials_groups: list[dict] = []
    layers_summary: list[dict] = []
    total_colorable_liters = 0.0

    for idx, layer in enumerate(system["layers"], start=1):
        group_items: list[dict] = []
        layer_product_names: list[str] = []

        for product_spec in layer["products"]:
            pid = _resolve_product_id(product_spec, color_type, finish_override, grade_override)
            product = PRODUCTS.get(pid)
            if not product:
                raise ValueError(f"Product not in catalog: {pid}")

            multiplier = product_spec.get("multiplier", 1)
            needed_m2 = working_area * multiplier

            combo = _best_pack_combination(needed_m2, product["packs"])

            for item in combo:
                pack = item["pack"]
                qty = item["qty"]
                line_total = qty * pack["price"]
                group_items.append({
                    "name": product["display_name"],
                    "package": pack["label"],
                    "quantity": qty,
                    "unit_price": pack["price"],
                    "total": line_total,
                })
                if colorant_included and product["colorable"]:
                    total_colorable_liters += qty * pack["volume_l"]

            layer_product_names.append(product["display_name"])

        group_label = f"Layer {_roman(idx)} — {layer['category']}"
        materials_groups.append({
            "group": group_label,
            "items": group_items,
        })

        layers_summary.append({
            "layer_num": idx,
            "category": layer["category"],
            "main_product": " + ".join(layer_product_names),
            "description": layer["description"],
        })

    # ── колеровка отдельной строкой ───────────────────────────
    colorant_total = 0
    if colorant_included and total_colorable_liters > 0:
        rate = COLORANT["dark"] if color_type == "dark" else COLORANT["light"]
        colorant_liters = math.ceil(total_colorable_liters)
        colorant_total = int(colorant_liters * rate)
        materials_groups.append({
            "group": "Colorant",
            "items": [{
                "name": f"Tinting ({'dark base' if color_type == 'dark' else 'light base'})",
                "package": "л",
                "quantity": colorant_liters,
                "unit_price": rate,
                "total": colorant_total,
            }],
        })

    materials_total = sum(
        item["total"] for group in materials_groups for item in group["items"]
    )

    # ── работы ────────────────────────────────────────────────
    works_total = 0
    application_rate = system["rate_thb_m2"]
    if application_included:
        min_area = system.get("min_area_m2_for_works") or 0
        if area < min_area:
            # для airless красок ниже минимума — работы не включаем
            application_included = False
        else:
            works_total = int(area * application_rate)

    total = materials_total + works_total
    price_per_sqm = int(round(total / area)) if area else 0

    # ── копирайт-плейсхолдеры (генерится отдельно через Claude) ──
    color_name, color_hex = _format_color_name(color_type, intent.get("color_name"))
    benefits = _benefits_for_system(system, intent.get("zone", ""))

    return {
        "system_id": system_id,
        "client_name": client_name,
        "product_title": system["display_name"],
        "product_subtitle": system["subtitle"],
        "product_description": intent.get(
            "product_description",
            f"{system['display_name']} — premium {system.get('chemistry', '')} system, "
            f"applied in {len(system['layers'])} layers with the {system['tool']} technique.",
        ),
        "design_intent": intent.get("design_intent", "Surfaces that hold light, depth, and quiet luxury."),
        "area": area,
        "working_area": round(working_area, 1),
        "zone": intent.get("zone", "Interior"),
        "color_type": color_type,
        "color_name": color_name,
        "color_hex": color_hex,
        "application_included": application_included,
        "application_rate": application_rate,
        "layers": layers_summary,
        "materials": materials_groups,
        "materials_total": int(materials_total),
        "colorant_total": int(colorant_total),
        "works_total": int(works_total),
        "total": int(total),
        "price_per_sqm": price_per_sqm,
        "benefits": benefits,
        "date": datetime.now().strftime("%d.%m.%Y"),
        # photos — добавляются в bot.py отдельно
        "photos": intent.get("photos", []),
    }


def compute_custom_kp(intent: dict) -> dict:
    """
    Расчёт нестандартного КП (изделия, большие образцы, произвольные позиции).
    Цены приходят только от пользователя — никаких прайсов и запасов.
    """
    items_in = intent.get("items") or []
    if not items_in:
        raise ValueError("No items found — please list what to quote and the prices")

    missing = [it.get("name") or "?" for it in items_in if not it.get("unit_price")]
    if missing:
        raise ValueError("Price not specified for: " + ", ".join(missing))

    rows = []
    items_count = 0
    for it in items_in:
        qty = float(it.get("quantity") or 1)
        unit_price = float(it["unit_price"])
        line_total = int(round(qty * unit_price))
        rows.append({
            "name": it.get("name") or "Item",
            "package": it.get("unit") or "pcs",
            "quantity": int(qty) if qty == int(qty) else qty,
            "unit_price": int(round(unit_price)),
            "total": line_total,
        })
        items_count += qty

    materials_total = sum(r["total"] for r in rows)
    title = intent.get("title") or "Bespoke Proposal"

    return {
        "is_custom": True,
        "system_id": None,
        "client_name": intent.get("client_name"),
        "product_title": title,
        "product_subtitle": "Bespoke Commission",
        "product_description": intent.get(
            "product_description",
            f"{title} — crafted individually by Pratta Thailand masters "
            "with authentic Italian materials, made to order for your project.",
        ),
        "design_intent": intent.get("design_intent", "Made by hand, made to order."),
        "area": None,
        "working_area": None,
        "zone": None,
        "color_type": None,
        "color_name": None,
        "color_hex": None,
        "application_included": False,
        "application_rate": 0,
        "layers": [],
        "materials": [{"group": "Bespoke Items", "items": rows}],
        "materials_total": int(materials_total),
        "colorant_total": 0,
        "works_total": 0,
        "total": int(materials_total),
        "price_per_sqm": 0,
        "items_count": int(items_count) if items_count == int(items_count) else items_count,
        "notes": intent.get("notes"),
        "benefits": [
            "Handcrafted by Pratta masters",
            "Authentic Italian raw materials",
            "Made to order",
        ],
        "date": datetime.now().strftime("%d.%m.%Y"),
        "photos": intent.get("photos", []),
    }


def _roman(n: int) -> str:
    return {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(n, str(n))


def apply_refinement(prev_intent: dict, refinement_intent: dict) -> dict:
    """Слить refinement поверх prev_intent — для итеративных правок менеджера."""
    merged = dict(prev_intent)
    for k, v in refinement_intent.items():
        if v is not None and v != "":
            merged[k] = v
    return merged


if __name__ == "__main__":
    # Self-test: тот самый кейс с 15 л Ruvido
    print("─ TEST: Manu 75 m² light ─")
    kp = compute_kp({
        "system": "manu",
        "area": 75,
        "zone": "Interior",
        "color_type": "light",
        "application_included": True,
    })
    for g in kp["materials"]:
        print(f"\n[{g['group']}]")
        for it in g["items"]:
            print(f"  {it['name']:<25} {it['package']:<6} ×{it['quantity']:<3} = {it['total']:>8} THB")
    print(f"\nMaterials: {kp['materials_total']:>10} THB")
    print(f"Works:     {kp['works_total']:>10} THB")
    print(f"TOTAL:     {kp['total']:>10} THB")
    print(f"per m²:    {kp['price_per_sqm']:>10} THB/m²")

    print("\n\n─ TEST: Travertino Imperium 50 m² dark ─")
    kp2 = compute_kp({
        "system": "travertino_imperium",
        "area": 50,
        "zone": "Interior",
        "color_type": "dark",
        "finish": "metalline_gold",
        "application_included": True,
    })
    for g in kp2["materials"]:
        print(f"\n[{g['group']}]")
        for it in g["items"]:
            print(f"  {it['name']:<25} {it['package']:<6} ×{it['quantity']:<3} = {it['total']:>8} THB")
    print(f"\nMaterials: {kp2['materials_total']:>10} THB")
    print(f"Works:     {kp2['works_total']:>10} THB")
    print(f"TOTAL:     {kp2['total']:>10} THB")
