# Pratta KP Bot — @Commercialprattabot

Телеграм-бот для менеджеров: получает описание задачи (текст / голос / фото) → собирает структурированный запрос → считает КП → отдаёт PDF в стиле Villa Vanilla.

## Архитектура

```
TG message ─► bot.py  ── parse_intent ──►  Claude (Sonnet 4.6)
                  │                              │
                  │                              ▼
                  │                         intent JSON
                  │                              │
                  ├── compute_kp() ◄─────────────┤  ← вся арифметика в Python (calculator.py)
                  │       │
                  │       ▼
                  │   kp_data (deterministic)
                  │       │
                  ├── generate_copy() ──► Claude (креатив: цвет, описание, цитата)
                  │       │
                  │       ▼
                  │   kp_data + photos
                  │       │
                  └── generate_kp_pdf() ──► WeasyPrint ──► PDF (Villa Vanilla)
```

## Файлы

| Файл | Что |
|------|-----|
| `bot.py` | Telegram ConversationHandler · фото, голос, текст, инлайн-кнопки |
| `catalog.py` | Каталог продуктов (упаковки, выходы, цены) + системы (слои) |
| `calculator.py` | Детерминированный расчёт КП по формуле `ceil(area×1.10 / yield)` с оптимальным подбором упаковок |
| `claude_handler.py` | Claude используется **только** для парсинга intent и креатива (без арифметики) |
| `pdf_generator.py` | WeasyPrint + base64 фото в data URI |
| `templates/kp.html` | 5-6 страниц в стиле Villa Vanilla (песочный + охра, Cormorant Garamond + Jost) |

## Что умеет

- Свободный текст или голосовое (RU/EN/TH)
- Парсинг продукта/площади/цвета/финиша/нанесения через Claude
- Детерминированный расчёт через `calculator.py`:
  - оптимальный подбор упаковок (брутфорс — гарантированно дешевле)
  - 10% запас на площадь
  - корректные множители на проходы (Intonachino ×2, Manu/Travertino — yield уже на 2 слоя)
  - колеровка отдельной строкой (95/195 THB/л; Fondo a Calce не колеруется)
- Инкрементальные правки: «увеличь до 200 м²», «замени финиш на silver», «без нанесения», «клиент Ivan» — Claude применяет поверх предыдущего intent
- Фото проекта (до 6 шт) — отдельная страница «Project Reference» в PDF
- Команды: `/start`, `/reset`

## Поддерживаемые системы

Известковые: Travertino Imperium, Velvet, Intonachino (Fine/Medium/Coarse), Marmorino Carrara
Акриловые текстурные: Seta Stucco, Roccia, Loft, Sequoia
Венецианские: Antico Veneziano
Кистевые: Manu, Sirocco, Phantom, Seta Exclusive, Antico Velluto, Dolce Seta, Shabby, Fantasia
Краски: Plastogum, INT&EST, Theia Eggshell

Источник прайса: `/Pratta_System/03_Pricing/pricelist_SL.md`. При изменении прайса — править `catalog.py`.

## Деплой

### Локально
```bash
brew install weasyprint
pip install -r requirements.txt
cp .env.example .env  # вставить TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY
python bot.py
```

### Railway / Docker
`Dockerfile` уже настроен — деплоить как есть. Env:
- `TELEGRAM_BOT_TOKEN`
- `ANTHROPIC_API_KEY`

## Использование менеджерами

1. Открыть @Commercialprattabot в Telegram
2. Написать: «Клиент Ivan — Travertino Imperium, 150 м², светлый, под ключ»
3. Бот показывает сводку с кнопками:
   - ✅ Сгенерировать PDF
   - ✏️ Изменить расчёт (одной фразой)
   - 📷 Добавить фото
4. Можно сразу прислать фото — попадут в PDF отдельной страницей
5. Нажать ✅ → получить PDF → отправить клиенту

## Что в стиле Villa Vanilla (PDF)

- Бумага `#F4ECD8`, акцент-охра `#9C7A47`
- Cormorant Garamond (заголовки), Jost (тело)
- Декоративные уголки на каждой странице
- Круглая печать «Pratta Exclusive» на обложке
- Те же визуальные правила, что у Doc Generator (Quotation/Invoice/...) — единый бренд

## Известные ограничения

- Голос распознаётся через Google STT (бесплатно, не идеально). Можно заменить на Whisper API.
- Бот не интегрирован с CRM Bitrix24 — PDF не падает в timeline сделки автоматически. План: при работающей интеграции добавить поле `deal_id` в intent и upload через `crm.timeline.comment.add`.
- Photo-страница рассчитана на jpg/png. Если прислать больше 6 фото — лишние игнорируются.
