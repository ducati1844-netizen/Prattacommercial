"""
Каталог продуктов и систем Pratta Thailand.
Источник: /Pratta_System/03_Pricing/pricelist_SL.md + /Pratta_System/02_Systems/
Все цены SL retail в THB. Обновлено 2025-08-03.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# ПРОДУКТЫ — упаковки, выходы, цены
# ─────────────────────────────────────────────────────────────
# pack: {"label": шильд для PDF, "volume_l": объём в литрах,
#        "yield_m2": выход одного пакета в м², "price": цена THB}

PRODUCTS = {
    # ── ПРАЙМЕРЫ И ПОДГОТОВКА ─────────────────────────────────
    "primer_normal": {
        "display_name": "Primer Normal",
        "category": "primer",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 90,  "price": 1500},
            {"label": "5 л", "volume_l": 5, "yield_m2": 450, "price": 3800},
        ],
    },
    "ruvido_pt": {
        "display_name": "Ruvido P/T",
        "category": "primer",
        "colorable": True,
        "packs": [
            {"label": "1 л",  "volume_l": 1,  "yield_m2": 10,  "price": 1800},
            {"label": "4 л",  "volume_l": 4,  "yield_m2": 40,  "price": 5760},
            {"label": "15 л", "volume_l": 15, "yield_m2": 150, "price": 14600},
        ],
    },
    "ruvido_da": {
        "display_name": "Ruvido D/A",
        "category": "primer",
        "colorable": True,
        "packs": [
            {"label": "1 л",  "volume_l": 1,  "yield_m2": 10,  "price": 1700},
            {"label": "4 л",  "volume_l": 4,  "yield_m2": 40,  "price": 4650},
            {"label": "15 л", "volume_l": 15, "yield_m2": 150, "price": 13200},
        ],
    },
    "primer_liscio_pt": {
        "display_name": "Primer Liscio P/T",
        "category": "primer",
        "colorable": True,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 10, "price": 1800},
            {"label": "4 л", "volume_l": 4, "yield_m2": 40, "price": 5650},
        ],
    },
    "primer_liscio_da": {
        "display_name": "Primer Liscio D/A",
        "category": "primer",
        "colorable": True,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 10, "price": 1600},
            {"label": "4 л", "volume_l": 4, "yield_m2": 40, "price": 5070},
        ],
    },
    "fondo_a_calce": {
        "display_name": "Fondo a Calce",
        "category": "primer",
        "colorable": False,  # известковый, не колеруется
        "packs": [
            {"label": "1 л",  "volume_l": 1,  "yield_m2": 10,  "price": 1400},
            {"label": "4 л",  "volume_l": 4,  "yield_m2": 40,  "price": 5800},
            {"label": "15 л", "volume_l": 15, "yield_m2": 150, "price": 12300},
        ],
    },

    # ── ДЕКОРАТИВНЫЕ — ТЕКСТУРНЫЕ ────────────────────────────
    "travertino_imperium": {
        "display_name": "Travertino Imperium",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 6,  "price": 4000},
            {"label": "24 л", "volume_l": 24, "yield_m2": 24, "price": 14300},
        ],
    },
    "velvet": {
        "display_name": "Velvet",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 6,  "price": 4800},
            {"label": "24 л", "volume_l": 24, "yield_m2": 24, "price": 15200},
        ],
    },
    "seta_stucco": {
        "display_name": "Seta Stucco",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 6,  "price": 5200},
            {"label": "24 л", "volume_l": 24, "yield_m2": 24, "price": 18000},
        ],
    },
    "roccia": {
        "display_name": "Roccia",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 4,  "price": 4000},
            {"label": "24 л", "volume_l": 24, "yield_m2": 17, "price": 12800},
        ],
    },
    "intonachino_fine": {
        "display_name": "Intonachino Fine",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "24 л", "volume_l": 24, "yield_m2": 24, "price": 13800},
        ],
    },
    "intonachino_medium": {
        "display_name": "Intonachino Medium",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "24 л", "volume_l": 24, "yield_m2": 17, "price": 13800},
        ],
    },
    "intonachino_coarse": {
        "display_name": "Intonachino Coarse",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "24 л", "volume_l": 24, "yield_m2": 12, "price": 13800},
        ],
    },
    "loft": {
        "display_name": "Loft",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 3,  "price": 4600},
            {"label": "24 л", "volume_l": 24, "yield_m2": 12, "price": 15200},
        ],
    },
    "sequoia": {
        "display_name": "Sequoia",
        "category": "plaster_textured",
        "colorable": True,
        "packs": [
            {"label": "24 л", "volume_l": 24, "yield_m2": 12, "price": 12000},
        ],
    },

    # ── ВЕНЕЦИАНСКИЕ ──────────────────────────────────────────
    "antico_veneziano": {
        "display_name": "Antico Veneziano",
        "category": "plaster_venetian",
        "colorable": True,
        "packs": [
            {"label": "1 л",  "volume_l": 1,  "yield_m2": 5,   "price": 1400},
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 30,  "price": 7200},
            {"label": "24 л", "volume_l": 24, "yield_m2": 120, "price": 24400},
        ],
    },
    "marmorino_carrara": {
        "display_name": "Marmorino Carrara",
        "category": "plaster_venetian",
        "colorable": True,
        "packs": [
            {"label": "6 л",  "volume_l": 6,  "yield_m2": 9,  "price": 4400},
            {"label": "24 л", "volume_l": 24, "yield_m2": 36, "price": 14800},
        ],
    },

    # ── SILK LINE (кисть) ─────────────────────────────────────
    "manu": {
        "display_name": "Manu",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л",  "volume_l": 4,  "yield_m2": 20, "price": 8000},
            {"label": "12 л", "volume_l": 12, "yield_m2": 60, "price": 19200},
        ],
    },
    "sirocco": {
        "display_name": "Sirocco",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 8000},
        ],
    },
    "shabby": {
        "display_name": "Shabby",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 9800},
        ],
    },
    "phantom": {
        "display_name": "Phantom",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 24, "price": 9200},
        ],
    },
    "phantom_nuance": {
        "display_name": "Phantom Nuance",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 24, "price": 10800},
        ],
    },
    "seta_exclusive": {
        "display_name": "Seta Exclusive",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 24, "price": 9800},
        ],
    },
    "antico_velluto": {
        "display_name": "Antico Velluto",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 9600},
        ],
    },
    "dolce_seta": {
        "display_name": "Dolce Seta",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 8000},
        ],
    },
    "fantasia": {
        "display_name": "Fantasia",
        "category": "plaster_brush",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 9200},
        ],
    },

    # ── КРАСКИ ────────────────────────────────────────────────
    "plastogum_pt": {
        "display_name": "Plastogum P/T",
        "category": "paint",
        "colorable": True,
        "packs": [
            {"label": "15 л", "volume_l": 15, "yield_m2": 90, "price": 9600},
        ],
    },
    "plastogum_da": {
        "display_name": "Plastogum D/A",
        "category": "paint",
        "colorable": True,
        "packs": [
            {"label": "15 л", "volume_l": 15, "yield_m2": 90, "price": 9400},
        ],
    },
    "int_est_pt": {
        "display_name": "INT&EST P/T",
        "category": "paint",
        "colorable": True,
        "packs": [
            {"label": "15 л", "volume_l": 15, "yield_m2": 105, "price": 7600},
        ],
    },
    "theia_eggshell_pt": {
        "display_name": "Theia Eggshell P/T",
        "category": "paint",
        "colorable": True,
        "packs": [
            {"label": "15 л", "volume_l": 15, "yield_m2": 105, "price": 12900},
        ],
    },

    # ── ФИНИШИ ────────────────────────────────────────────────
    "metalline_gold": {
        "display_name": "Metalline Gold",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 9,  "price": 2400},
            {"label": "4 л", "volume_l": 4, "yield_m2": 36, "price": 10400},
        ],
    },
    "metalline_silver": {
        "display_name": "Metalline Silver",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 9,  "price": 2400},
            {"label": "4 л", "volume_l": 4, "yield_m2": 36, "price": 9800},
        ],
    },
    "metalline_bronze": {
        "display_name": "Metalline Bronze",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 9,  "price": 2400},
            {"label": "4 л", "volume_l": 4, "yield_m2": 36, "price": 10400},
        ],
    },
    "specchio_cera": {
        "display_name": "Specchio Cera",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 30, "price": 4100},
        ],
    },
    "umbrella_silk": {
        "display_name": "Umbrella Silk",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "1 л", "volume_l": 1, "yield_m2": 10, "price": 1850},
        ],
    },
    "umbrella": {
        "display_name": "Umbrella",
        "category": "finish",
        "colorable": False,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 40, "price": 5900},
        ],
    },
    "velatura": {
        "display_name": "Velatura",
        "category": "finish",
        "colorable": True,
        "packs": [
            {"label": "4 л", "volume_l": 4, "yield_m2": 32, "price": 5600},
        ],
    },
}


# ─────────────────────────────────────────────────────────────
# СИСТЕМЫ — структура слоёв
# ─────────────────────────────────────────────────────────────
# layer.products[i].multiplier — на сколько умножать рабочую площадь
# (учитывает «×N проходов»). Если выход уже включает все слои — multiplier=1.
# primer_family — name → resolves to {family}_pt или {family}_da по color_type.

def _by_tone(family):
    """Возвращает функцию, которая по color_type вернёт нужный продукт."""
    return ("variant_by_tone", family)


SYSTEMS = {
    # ── ИЗВЕСТКОВЫЕ ──────────────────────────────────────────
    "travertino_imperium": {
        "display_name": "Travertino Imperium",
        "subtitle": "Natural Lime Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "lime",
        "medical_certified": True,
        "default_finish": "velatura",
        "available_finishes": ["velatura", "metalline_gold", "metalline_silver", "metalline_bronze", "umbrella"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "fondo_a_calce", "multiplier": 1},
                ],
                "description": "Mineral primer and lime adhesion layer ensure a stable, breathable foundation.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "travertino_imperium", "multiplier": 1}],  # yield includes 2 layers
                "description": "Italian lime plaster applied in two passes, revealing the depth and movement of natural travertine stone.",
            },
            {
                "category": "Finish",
                "products": [{"id": "velatura", "multiplier": 1, "is_finish": True}],
                "description": "Decorative veil seals the lime surface and deepens its tonal patina.",
            },
        ],
    },
    "velvet": {
        "display_name": "Velvet",
        "subtitle": "Lime Velvet Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "lime",
        "medical_certified": True,
        "default_finish": "velatura",
        "available_finishes": ["velatura", "specchio_cera", "metalline_gold", "metalline_silver"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "fondo_a_calce", "multiplier": 1},
                ],
                "description": "Mineral primer and lime base prepare a breathable, mineral surface.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "velvet", "multiplier": 1}],
                "description": "Polished lime plaster with a soft, tactile velvet finish.",
            },
            {
                "category": "Finish",
                "products": [{"id": "velatura", "multiplier": 1, "is_finish": True}],
                "description": "Decorative veil seals the velvet surface and softens its tone.",
            },
        ],
    },
    "intonachino": {
        "display_name": "Intonachino",
        "subtitle": "Mineral Texture Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "lime",
        "medical_certified": True,
        "default_finish": "velatura",
        "available_finishes": ["velatura", "umbrella", "metalline_gold"],
        "default_grade": "intonachino_medium",
        "available_grades": ["intonachino_fine", "intonachino_medium", "intonachino_coarse"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "fondo_a_calce", "multiplier": 1},
                ],
                "description": "Mineral primer and lime base for breathable bonding.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "intonachino_medium", "multiplier": 2, "is_grade": True}],  # ×2 passes
                "description": "Mineral lime render applied in two passes — natural matte texture.",
            },
            {
                "category": "Finish",
                "products": [{"id": "velatura", "multiplier": 1, "is_finish": True}],
                "description": "Decorative veil or protective umbrella seals the texture.",
            },
        ],
    },
    "marmorino_carrara": {
        "display_name": "Marmorino Carrara",
        "subtitle": "Polished Lime Marble",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "lime",
        "medical_certified": True,
        "default_finish": "velatura",
        "available_finishes": ["velatura", "specchio_cera", "metalline_gold", "metalline_silver"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Smooth primer and bonding layer for polished application.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "marmorino_carrara", "multiplier": 1}],
                "description": "Italian lime marble plaster — polished to a soft pearlescent sheen.",
            },
            {
                "category": "Finish",
                "products": [{"id": "velatura", "multiplier": 1, "is_finish": True}],
                "description": "Decorative veil seals the marble surface and softens its tonal depth.",
            },
        ],
    },
    "antico_veneziano": {
        "display_name": "Antico Veneziano",
        "subtitle": "Mirror-Polished Venetian",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "specchio_cera",
        "available_finishes": ["specchio_cera"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Smooth primer prepares the surface for high-gloss venetian.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "antico_veneziano", "multiplier": 1}],  # yield includes 3-4 passes
                "description": "Classical venetian plaster applied in three to four passes — true mirror polish.",
            },
            {
                "category": "Finish",
                "products": [{"id": "specchio_cera", "multiplier": 1, "is_finish": True}],
                "description": "Mirror wax — essential for the high-gloss Venetian effect.",
            },
        ],
    },
    # ── АКРИЛОВЫЕ ТЕКСТУРНЫЕ ─────────────────────────────────
    "seta_stucco": {
        "display_name": "Seta Stucco",
        "subtitle": "Industrial Loft Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "acrylic",
        "medical_certified": True,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk", "metalline_silver", "metalline_gold", "metalline_bronze", "velatura"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Acrylic primer and bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "seta_stucco", "multiplier": 1}],
                "description": "Polished concrete-look plaster with soft metallic depth.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil — locks in the surface and adds a soft satin sheen.",
            },
        ],
    },
    "roccia": {
        "display_name": "Roccia",
        "subtitle": "Natural Stone Texture",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "metalline_gold",
        "available_finishes": ["metalline_gold", "metalline_silver", "velatura"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Acrylic primer and bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "roccia", "multiplier": 1}],
                "description": "Heavily textured plaster — bold natural rock relief.",
            },
            {
                "category": "Finish",
                "products": [{"id": "metalline_gold", "multiplier": 1, "is_finish": True}],
                "description": "Metallic glaze highlights the stone relief.",
            },
        ],
    },
    "loft": {
        "display_name": "Loft",
        "subtitle": "Urban Concrete Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "metalline_silver",
        "available_finishes": ["metalline_silver", "metalline_gold", "velatura"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Acrylic primer and bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "loft", "multiplier": 1}],
                "description": "Industrial concrete-effect plaster with rough urban character.",
            },
            {
                "category": "Finish",
                "products": [{"id": "metalline_silver", "multiplier": 1, "is_finish": True}],
                "description": "Metallic accent finish.",
            },
        ],
    },
    "sequoia": {
        "display_name": "Sequoia",
        "subtitle": "Bark Texture Collection",
        "tool": "trowel",
        "rate_thb_m2": 1300,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "metalline_gold",
        "available_finishes": ["metalline_gold", "metalline_silver", "velatura"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Acrylic primer and bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "sequoia", "multiplier": 1}],
                "description": "Deep bark-effect texture — wild natural relief.",
            },
            {
                "category": "Finish",
                "products": [{"id": "metalline_gold", "multiplier": 1, "is_finish": True}],
                "description": "Metallic glaze brings out the relief.",
            },
        ],
    },
    # ── КИСТЕВЫЕ — SILK LINE ─────────────────────────────────
    "manu": {
        "display_name": "Manu",
        "subtitle": "Brush Velvet Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": None,
        "available_finishes": [],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "ruvido_pt", "multiplier": 2, "by_tone": "ruvido"},  # 2 layers
                ],
                "description": "Mineral primer and Ruvido textured base — two layers for adhesion and depth.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "manu", "multiplier": 1}],  # yield 60м² already covers 2 layers
                "description": "Soft brush velvet finish, applied in two passes — rich tactile sheen.",
            },
        ],
    },
    "sirocco": {
        "display_name": "Sirocco",
        "subtitle": "Brush Silk Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "sirocco", "multiplier": 1}],
                "description": "Silky brush-applied finish with iridescent shimmer.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "phantom": {
        "display_name": "Phantom",
        "subtitle": "Silk Line Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "phantom", "multiplier": 1}],
                "description": "Silky brush finish with subtle silver reflection.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "seta_exclusive": {
        "display_name": "Seta Exclusive",
        "subtitle": "Silk Line Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "seta_exclusive", "multiplier": 1}],
                "description": "Premium silk-effect brush finish — refined and luminous.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "antico_velluto": {
        "display_name": "Antico Velluto",
        "subtitle": "Silk Line Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "antico_velluto", "multiplier": 1}],
                "description": "Aged velvet brush finish — warm depth and texture.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "dolce_seta": {
        "display_name": "Dolce Seta",
        "subtitle": "Silk Line Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "dolce_seta", "multiplier": 1}],
                "description": "Soft silk brush finish with delicate luster.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "shabby": {
        "display_name": "Shabby",
        "subtitle": "Brush Silk Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "shabby", "multiplier": 1}],
                "description": "Vintage shabby-look brush finish with antiqued character.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    "fantasia": {
        "display_name": "Fantasia",
        "subtitle": "Brush Glitter Collection",
        "tool": "brush",
        "rate_thb_m2": 650,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": "umbrella_silk",
        "available_finishes": ["umbrella_silk"],
        "layers": [
            {
                "category": "Preparation",
                "products": [
                    {"id": "primer_normal", "multiplier": 1},
                    {"id": "primer_liscio_pt", "multiplier": 1, "by_tone": "primer_liscio"},
                ],
                "description": "Primer and smooth bonding layer.",
            },
            {
                "category": "Decorative Base",
                "products": [{"id": "fantasia", "multiplier": 1}],
                "description": "Sparkling brush finish with fine glitter shimmer.",
            },
            {
                "category": "Finish",
                "products": [{"id": "umbrella_silk", "multiplier": 1, "is_finish": True}],
                "description": "Protective silk veil.",
            },
        ],
    },
    # ── КРАСКИ ───────────────────────────────────────────────
    "plastogum": {
        "display_name": "Plastogum",
        "subtitle": "Elastomeric Coating",
        "tool": "airless",
        "rate_thb_m2": 500,
        "chemistry": "acrylic",
        "medical_certified": True,
        "default_finish": None,
        "available_finishes": [],
        "min_area_m2_for_works": 300,
        "layers": [
            {
                "category": "Preparation",
                "products": [{"id": "primer_normal", "multiplier": 1}],
                "description": "Mineral primer for adhesion.",
            },
            {
                "category": "Coating",
                "products": [{"id": "plastogum_pt", "multiplier": 2, "by_tone": "plastogum"}],  # ×2 layers
                "description": "Elastomeric paint applied in two coats — waterproof and breathable.",
            },
        ],
    },
    "int_est": {
        "display_name": "INT&EST",
        "subtitle": "Interior + Exterior Acrylic",
        "tool": "airless",
        "rate_thb_m2": 500,
        "chemistry": "acrylic",
        "medical_certified": False,
        "default_finish": None,
        "available_finishes": [],
        "min_area_m2_for_works": 300,
        "layers": [
            {
                "category": "Preparation",
                "products": [{"id": "primer_normal", "multiplier": 1}],
                "description": "Mineral primer for adhesion.",
            },
            {
                "category": "Coating",
                "products": [{"id": "int_est_pt", "multiplier": 2}],  # ×2 layers
                "description": "Two coats of acrylic paint.",
            },
        ],
    },
    "theia": {
        "display_name": "Theia Eggshell",
        "subtitle": "Eggshell Interior Paint",
        "tool": "airless",
        "rate_thb_m2": 500,
        "chemistry": "acrylic",
        "medical_certified": True,
        "default_finish": None,
        "available_finishes": [],
        "min_area_m2_for_works": 300,
        "layers": [
            {
                "category": "Preparation",
                "products": [{"id": "primer_normal", "multiplier": 1}],
                "description": "Mineral primer for adhesion.",
            },
            {
                "category": "Coating",
                "products": [{"id": "theia_eggshell_pt", "multiplier": 2}],
                "description": "Two coats of medical-grade eggshell paint.",
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────
# КОЛЕРОВКА
# ─────────────────────────────────────────────────────────────
COLORANT = {
    "light": 95,   # THB/л
    "dark":  195,  # THB/л
}


# ─────────────────────────────────────────────────────────────
# ВЫРАВНИВАНИЕ ИМЁН СИСТЕМ — алиасы для парсера
# ─────────────────────────────────────────────────────────────
SYSTEM_ALIASES = {
    "travertino": "travertino_imperium",
    "travertino imperium": "travertino_imperium",
    "travertin": "travertino_imperium",
    "imperium": "travertino_imperium",
    "velvet": "velvet",
    "вельвет": "velvet",
    "manu": "manu",
    "ману": "manu",
    "intonachino": "intonachino",
    "интонакино": "intonachino",
    "intonachino fine": "intonachino",
    "intonachino medium": "intonachino",
    "intonachino coarse": "intonachino",
    "marmorino": "marmorino_carrara",
    "marmorino carrara": "marmorino_carrara",
    "carrara": "marmorino_carrara",
    "antico veneziano": "antico_veneziano",
    "veneziano": "antico_veneziano",
    "венецианка": "antico_veneziano",
    "seta stucco": "seta_stucco",
    "сета стукко": "seta_stucco",
    "roccia": "roccia",
    "роччиа": "roccia",
    "loft": "loft",
    "лофт": "loft",
    "sequoia": "sequoia",
    "сиквойя": "sequoia",
    "sirocco": "sirocco",
    "сирокко": "sirocco",
    "phantom": "phantom",
    "фантом": "phantom",
    "seta exclusive": "seta_exclusive",
    "seta": "seta_exclusive",
    "antico velluto": "antico_velluto",
    "velluto": "antico_velluto",
    "dolce seta": "dolce_seta",
    "dolce": "dolce_seta",
    "shabby": "shabby",
    "шебби": "shabby",
    "fantasia": "fantasia",
    "фантазия": "fantasia",
    "plastogum": "plastogum",
    "пластогум": "plastogum",
    "int est": "int_est",
    "int&est": "int_est",
    "int_est": "int_est",
    "theia": "theia",
    "тея": "theia",
}


def resolve_system(name: str) -> str | None:
    """Привести входное имя продукта/системы к ID в SYSTEMS."""
    if not name:
        return None
    key = name.lower().strip().replace("_", " ")
    if key in SYSTEM_ALIASES:
        return SYSTEM_ALIASES[key]
    if key in SYSTEMS:
        return key
    return None


def resolve_finish(name: str | None) -> str | None:
    if not name:
        return None
    key = name.lower().strip().replace(" ", "_")
    aliases = {
        "gold": "metalline_gold", "metalline_gold": "metalline_gold",
        "silver": "metalline_silver", "metalline_silver": "metalline_silver",
        "bronze": "metalline_bronze", "metalline_bronze": "metalline_bronze",
        "specchio": "specchio_cera", "specchio_cera": "specchio_cera", "wax": "specchio_cera",
        "velatura": "velatura",
        "umbrella": "umbrella", "umbrella_silk": "umbrella_silk",
    }
    return aliases.get(key)


def all_systems_list() -> list[str]:
    return sorted(SYSTEMS.keys())
