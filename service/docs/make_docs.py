#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_docs.py — генератор документации проекта из шаблона.

Собирает из словаря DOCS:
  README.md, ARCHITECTURE.md, DIGEST.md, CHANGELOG.md, DEVLOG.md,
  TODO.md, AI_BRIEF.md, QWEN.md — в корень проекта;
  USER_MANUAL.md + USER_MANUAL.docx + USER_MANUAL.pdf — в project_info/manuals/.

Запуск:  python service/docs/make_docs.py
Обычный запуск перезаписывает все файлы из DOCS: генератор — источник правды,
вручную документы не правятся. Бережный режим: --only-missing.

Для USER_MANUAL:
  • .docx собирается через python-docx (рендер markdown → docx);
  • .pdf — сначала через docx2pdf (Word), при неудаче — fpdf2 (manuals_to_pdf.py).
Если Word недоступен — PDF всё равно создаётся (fpdf2-fallback), но без логотипа.

Тексты правятся ТОЛЬКО в словаре DOCS этого файла.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _find_root(start: Path) -> Path:
    """Корень проекта: ближайший предок с .git; иначе папка скрипта."""
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start.parent


BASE_DIR = _find_root(Path(__file__).resolve())
MANUALS_DIR = BASE_DIR / "project_info" / "manuals"
ASSETS_DIR = BASE_DIR / "assets"

DOCS = {}

# ================================================================
# README.md
# ================================================================
DOCS["README.md"] = [
    "# ЗАПОЛНИТЬ: название проекта",
    "",
    "ЗАПОЛНИТЬ: один абзац — что это, зачем, для кого.",
    "",
    "## Быстрый старт",
    "",
    "```",
    "python -m venv venv",
    "venv\\Scripts\\activate        # Windows",
    "# source venv/bin/activate     # Linux/macOS",
    "pip install -r requirements.txt",
    "```",
    "",
    "Скопируйте `.env.example` в `.env` и заполните значения.",
    "",
    "ЗАПОЛНИТЬ: команда запуска и адрес/порт (например `python main.py`).",
    "",
    "## Структура",
    "",
    "- корень — боевой код (точка входа `main.py` и модули);",
    "- `assets/` — иконки, логотипы, шаблоны для сборки и работы;",
    "- `data/` — данные рантайма (в .gitignore): db, uploads, exports,",
    "  personal, big_files, reports, logs, temp;",
    "- `service/` — служебное: migrations, fixes, deploy, tools, docs;",
    "  запуск ТОЛЬКО через `python service/run.py service/...`;",
    "- `project_info/manuals/` — руководства пользователя (md + docx + pdf);",
    "- `project_info/ai_pack/` — упаковка для ИИ (`service/docs/ai_pack.py`);",
    "- `tests/` — тесты.",
    "",
    "## Сборка exe",
    "",
    "```",
    "build.bat     # результат: dist\\<ProjectName>\\<ProjectName>.exe",
    "```",
    "",
    "Перед сборкой `build.bat` автоматически генерирует документацию",
    "(включая PDF-инструкцию), собирает exe по `*.spec`.",
    "",
    "## Документация",
    "",
    "- `ARCHITECTURE.md` — устройство, схема БД, потоки данных.",
    "- `DIGEST.md` — короткий дайджест для быстрого входа в контекст.",
    "- `CHANGELOG.md` — история версий (строка на версию).",
    "- `DEVLOG.md` — журнал сессий разработки (включая неудачные ветки).",
    "- `TODO.md` — открытые задачи.",
    "- `AI_BRIEF.md` — правила и табу для ИИ-ассистентов.",
    "- `QWEN.md` — контекст и правила для AI-ассистента.",
    "- `project_info/manuals/USER_MANUAL.md` — инструкция пользователя (markdown).",
    "- `project_info/manuals/USER_MANUAL.docx` — Word-версия инструкции.",
    "- `project_info/manuals/USER_MANUAL.pdf` — PDF-инструкция (кнопка «?»).",
    "",
    "## Генераторы документации",
    "",
    "- `service/docs/make_docs.py` — собирает все .md-документы и",
    "  рендерит USER_MANUAL в docx + pdf.",
    "- `service/docs/manuals_to_pdf.py` — fallback md → pdf без Word (fpdf2).",
    "- `service/docs/ai_pack.py` — упаковка проекта для передачи в чат с ИИ.",
    "",
    "## Важно",
    "",
    "- `data/` (данные рантайма) не коммитится в git.",
    "- `.env` не коммитится, `.env.example` — коммитится как образец.",
    "- Документы проекта генерируются скриптами; правятся только в словаре DOCS.",
]

# ================================================================
# DIGEST.md
# ================================================================
DOCS["DIGEST.md"] = [
    "# DIGEST — дайджест проекта",
    "",
    "Короткая сводка для быстрого входа в контекст (люди и AI-ассистенты).",
    "",
    "## Суть",
    "",
    "- ЗАПОЛНИТЬ: 3-5 пунктов о главном (что за проект, для кого, какую",
    "  задачу решает).",
    "",
    "## Ключевые сущности",
    "",
    "- ЗАПОЛНИТЬ: основные таблицы/объекты/классы — одной строкой каждый.",
    "",
    "## Правила и оценки",
    "",
    "- ЗАПОЛНИТЬ: ключевые бизнес-правила, формулы, ограничения.",
    "",
    "## Где что лежит",
    "",
    "- `main.py` — точка входа.",
    "- `core/` — бизнес-логика (без GUI).",
    "- `gui/` — интерфейс (если есть).",
    "- `service/` — служебные скрипты (запуск через `service/run.py`).",
    "- `data/` — данные рантайма (вне git).",
    "- `assets/` — иконки, логотипы, шаблоны для сборки.",
    "- `project_info/` — руководства и упаковка для ИИ.",
    "",
    "## Деплой-статус",
    "",
    "- ЗАПОЛНИТЬ: где работает, какая версия, план переезда.",
    "",
    "## Ближайшие задачи",
    "",
    "- ЗАПОЛНИТЬ: 2-4 пункта.",
]

# ================================================================
# ARCHITECTURE.md
# ================================================================
DOCS["ARCHITECTURE.md"] = [
    "# ARCHITECTURE — ЗАПОЛНИТЬ: название проекта",
    "",
    "## 1. Цель",
    "",
    "- ЗАПОЛНИТЬ: какие задачи автоматизирует.",
    "",
    "## 2. Стек",
    "",
    "- ЗАПОЛНИТЬ: язык, фреймворк, БД, хостинг.",
    "- Python 3.13+ (шаблон рассчитан на современный Python).",
    "",
    "## 3. Структура",
    "",
    "```",
    "project/",
    "├── main.py                  # точка входа",
    "├── build.bat                # сборка exe (PyInstaller)",
    "├── <Project>.spec           # spec-файл PyInstaller",
    "├── config.json              # UI-настройки (опционально)",
    "├── requirements.txt         # зависимости",
    "│",
    "├── core/                    # бизнес-логика (без GUI)",
    "├── gui/                     # интерфейс (если есть)",
    "│",
    "├── assets/                  # иконки, логотипы, шаблоны для сборки",
    "├── service/                 # служебное (migrations, fixes, tools, docs)",
    "├── project_info/",
    "│   ├── manuals/             # USER_MANUAL.md + .docx + .pdf",
    "│   └── ai_pack/             # упаковка для ИИ (вне git)",
    "├── tests/",
    "└── data/                    # данные рантайма (вне git)",
    "```",
    "",
    "## 4. Схема БД",
    "",
    "- ЗАПОЛНИТЬ: таблицы и ключевые поля (или «БД нет»).",
    "",
    "## 5. Потоки данных",
    "",
    "- ЗАПОЛНИТЬ: основные сценарии по шагам.",
    "",
    "## 6. Роли и права",
    "",
    "- ЗАПОЛНИТЬ: роли и что им доступно.",
    "",
    "## 7. Миграции",
    "",
    "- История схемы — файлами `migrate_vX_Y.py` в `service/migrations/`;",
    "  все идемпотентны (проверки перед изменениями).",
    "- Запуск: `python service/run.py service/migrations/<файл>`.",
    "",
    "## 8. Безопасность",
    "",
    "- ЗАПОЛНИТЬ: пароли, токены, лимиты загрузки, журнал действий.",
    "- Секреты не хранятся в коде; `.env` не коммитится.",
]

# ================================================================
# CHANGELOG.md
# ================================================================
DOCS["CHANGELOG.md"] = [
    "# CHANGELOG",
    "",
    "## 0.1.0 — ЗАПОЛНИТЬ: дата",
    "",
    "- Проект начат из шаблона Template-open-python-project:",
    "  структура `data/`, `service/`, `project_info/`, `assets/`, `tests/`;",
    "  генераторы документации (`make_docs.py`, `ai_pack.py`), `run.py`.",
]

# ================================================================
# DEVLOG.md
# ================================================================
DOCS["DEVLOG.md"] = [
    "# DEVLOG — журнал сессий разработки",
    "",
    "Фиксируем ВСЁ, что делали, включая неудачные ветки. Цель — не потерять",
    "контекст и понимать, какие блоки кода в какой момент появлялись и пропадали.",
    "",
    "## Исходная точка",
    "",
    "- Проект развёрнут из шаблона Template-open-python-project.",
    "",
    "## Сессия — ЗАПОЛНИТЬ: дата",
    "",
    "- ЗАПОЛНИТЬ: что делали, что получилось, что сломалось.",
    "",
    "## Неудачные ветки и потери (важно!)",
    "",
    "- ЗАПОЛНИТЬ: что пробовали и откатили, чтобы не повторять.",
    "",
    "## Процессные выводы",
    "",
    "- Полные файлы давать только по явной просьбе.",
    "- После полной замены сверять маркеры (см. QWEN.md).",
    "- Ошибки Pylance — ранний индикатор поломки.",
    "- Если даются два варианта одного блока — брать последний (самый полный).",
]

# ================================================================
# TODO.md
# ================================================================
DOCS["TODO.md"] = [
    "# TODO — открытые задачи",
    "",
    "## Приоритет 1: доделать задуманное",
    "",
    "- [ ] ЗАПОЛНИТЬ: первая задача.",
    "",
    "## Приоритет 2: улучшить существующее",
    "",
    "- [ ] ЗАПОЛНИТЬ: улучшение.",
    "",
    "## Приоритет 3: документация и гигиена",
    "",
    "- [ ] Заполнить `AI_BRIEF.md` (стек, запуск, соглашения).",
    "- [ ] Заполнить `ARCHITECTURE.md` (схема, потоки, роли).",
    "- [ ] Заполнить `DIGEST.md` (3-5 пунктов о главном).",
    "- [ ] Прогнать `python service/docs/make_docs.py` после правок.",
    "",
    "## Отклонено (не делать)",
    "",
    "- ЗАПОЛНИТЬ: если что-то осознанно отклонили — зафиксировать здесь.",
]

# ================================================================
# AI_BRIEF.md
# ================================================================
DOCS["AI_BRIEF.md"] = [
    "# AI_BRIEF — правила работы с проектом",
    "",
    "Стек: ЗАПОЛНИТЬ: язык, фреймворк, БД, хостинг.",
    "Запуск: ЗАПОЛНИТЬ: точка входа, порт, команда.",
    "Тесты: ЗАПОЛНИТЬ: pytest / unittest, команда.",
    "Линтер: ЗАПОЛНИТЬ: ruff / flake8, команда.",
    "БД: изменения схемы — ТОЛЬКО новыми миграциями в `service/migrations/`,",
    "запуск через `python service/run.py service/migrations/<файл>`.",
    "",
    "## Табу",
    "",
    "- Не удалять данные без явного подтверждения пользователя.",
    "- Секреты не хранить в коде и не передавать в переписке; `.env` не коммитится.",
    "- Приватные данные (`data/`, `personal/`, дампы) — вне git и вне упаковок.",
    "- Шаблоны и большие функции править заменой целиком,",
    "  точечные правки — только с точными якорями.",
    "",
    "## Соглашения",
    "",
    "- ЗАПОЛНИТЬ: термины интерфейса, статусы, цветовые классы.",
    "",
    "## Статус",
    "",
    "- ЗАПОЛНИТЬ: текущая версия, что в бою, план.",
]

# ================================================================
# QWEN.md
# ================================================================
DOCS["QWEN.md"] = [
    "# QWEN.md — контекст ассистента по проекту",
    "",
    "## Пользователь и стиль",
    "",
    "- ЗАПОЛНИТЬ: кто пользователь, на каком языке общается, уровень.",
    "- Код: полные файлы ТОЛЬКО по явной просьбе; иначе точечные блоки",
    "  «найди/замени» с точными отступами (4 пробела на уровень).",
    "- Документы вести скриптами-генераторами (`service/docs/make_docs.py`).",
    "- Если даются два варианта одного блока — брать последний (самый полный).",
    "",
    "## Текущее состояние",
    "",
    "- Архитектура: см. `ARCHITECTURE.md`.",
    "- Журнал сессий и потери: см. `DEVLOG.md`. Открытые задачи: см. `TODO.md`.",
    "- Быстрый вход в контекст: см. `DIGEST.md`.",
    "",
    "## Маркеры целостности (проверять после каждой замены)",
    "",
    "- ЗАПОЛНИТЬ: список ключевых классов/функций/файлов, которые должны",
    "  быть на месте. Например, для GUI:",
    "  - `MainWindow.__init__`: self.tabs, self.tab_widgets, self.current_tab_id.",
    "  - `LeftPanel.set_editable(bool)`, `set_home_mode()`.",
    "  - `RightPanel.set_editable(bool)`.",
    "",
    "## Типовые ловушки",
    "",
    "- Полная замена файла теряет блоки — сверять маркеры.",
    "- Копипаст ломает отступы: методы выпадают из класса.",
    "- Pylance «not defined» — потерянный импорт.",
    "- ЗАПОЛНИТЬ: специфичные для проекта грабли.",
    "",
    "## Правила данных",
    "",
    "- ЗАПОЛНИТЬ: что является источником правды, что нельзя править задним",
    "  числом, что не коммитится.",
    "",
    "## Правила работы с документами",
    "",
    "- Тексты правятся ТОЛЬКО в словаре `DOCS` файла `service/docs/make_docs.py`.",
    "- Запуск: `python service/docs/make_docs.py` (перезапишет всё) или",
    "  `python service/docs/make_docs.py --only-missing`.",
    "- PDF и docx инструкции генерируются автоматически при запуске `make_docs.py`.",
]

# ================================================================
# USER_MANUAL.md — БЕЗ номеров в заголовках (нумерация — при рендере)
# ================================================================
DOCS["USER_MANUAL.md"] = [
    "# ЗАПОЛНИТЬ: инструкция пользователя",
    "",
    "## Что это и для кого",
    "",
    "ЗАПОЛНИТЬ: кратко — что за программа, для кого, какие задачи решает.",
    "",
    "## Первый запуск",
    "",
    "ЗАПОЛНИТЬ: что видит пользователь при первом запуске, что нужно настроить",
    "(папка данных, путь, порт и т.п.).",
    "",
    "## Окно программы",
    "",
    "ЗАПОЛНИТЬ: схема окна и основные элементы управления.",
    "",
    "## Основные сценарии",
    "",
    "### Сценарий 1 — ЗАПОЛНИТЬ: название",
    "",
    "ЗАПОЛНИТЬ: шаги по порядку.",
    "",
    "### Сценарий 2 — ЗАПОЛНИТЬ: название",
    "",
    "ЗАПОЛНИТЬ: шаги по порядку.",
    "",
    "## Настройки",
    "",
    "ЗАПОЛНИТЬ: какие настройки есть и что они меняют.",
    "",
    "## Резервное копирование",
    "",
    "ЗАПОЛНИТЬ: если есть автоматическое — как работает, где хранится,",
    "сколько копий. Если нет — указать, что делать вручную.",
    "",
    "## Частые вопросы",
    "",
    "- ЗАПОЛНИТЬ: вопрос → ответ.",
    "",
    "## В разработке (ближайшие версии)",
    "",
    "- ЗАПОЛНИТЬ: что планируется.",
]


# ================================================================
# РЕНДЕР MARKDOWN → DOCX
# ================================================================
_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]+",
    flags=re.UNICODE,
)


def _parse_md_blocks(text: str):
    """Markdown → список блоков (kind, payload).

    kinds: title, h2, h3, h4, p, bullet, code, table.
    Заголовки возвращаются БЕЗ номеров — нумерацию добавляет рендер.
    """
    blocks, buf, fence, table = [], [], False, []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if fence:
                blocks.append(("code", buf))
                buf = []
            fence = not fence
            continue
        if fence:
            buf.append(line)
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells if c):
                table.append(cells)
            continue
        if table:
            blocks.append(("table", table))
            table = []
        if not line.strip():
            continue
        if line.startswith("# "):
            blocks.append(("title", line[2:].strip()))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("#### "):
            blocks.append(("h4", line[5:].strip()))
        elif line.startswith("- "):
            blocks.append(("bullet", line[2:].strip()))
        else:
            blocks.append(("p", line.strip()))
    if table:
        blocks.append(("table", table))
    return blocks


def _find_logo() -> Path | None:
    """Логотип по цепочке: project_logo.png → project_logo.ico → logo.png → None."""
    for name in ("project_logo.png", "project_logo.ico",
                 "logo.png", "logo.ico"):
        p = ASSETS_DIR / name
        if p.exists():
            return p
    return None


def render_md_to_docx(md_path: Path, docx_path: Path) -> bool:
    """Рендерит markdown в docx с логотипом и авто-нумерацией заголовков."""
    try:
        from docx import Document
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("⚠️ python-docx не установлен — пропускаю docx")
        return False

    try:
        text = md_path.read_text(encoding="utf-8")
        blocks = _parse_md_blocks(text)

        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Times New Roman"
        style.font.size = Pt(12)
        for sec in doc.sections:
            sec.left_margin = Cm(2.5)
            sec.right_margin = Cm(1.5)
            sec.top_margin = Cm(2.0)
            sec.bottom_margin = Cm(2.0)

        logo = _find_logo()
        if logo:
            try:
                doc.add_picture(str(logo), width=Cm(5))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            except Exception as e:
                print(f"⚠️ Логотип не вставлен: {e}")

        n2 = n3 = n4 = 0

        for kind, payload in blocks:
            if kind == "title":
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(payload)
                r.bold = True
                r.font.size = Pt(18)
            elif kind == "h2":
                n2 += 1
                n3 = n4 = 0
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
                r = p.add_run(f"{n2}. {payload}")
                r.bold = True
                r.font.size = Pt(15)
            elif kind == "h3":
                n3 += 1
                n4 = 0
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                r = p.add_run(f"{n2}.{n3}. {payload}")
                r.bold = True
                r.font.size = Pt(13)
            elif kind == "h4":
                n4 += 1
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(4)
                r = p.add_run(f"{n2}.{n3}.{n4}. {payload}")
                r.bold = True
                r.font.size = Pt(12)
            elif kind == "p":
                clean = payload.replace("`", "")
                doc.add_paragraph(clean)
            elif kind == "bullet":
                clean = payload.replace("`", "")
                doc.add_paragraph(clean, style="List Bullet")
            elif kind == "code":
                for ln in payload:
                    p = doc.add_paragraph()
                    r = p.add_run(ln)
                    r.font.name = "Courier New"
                    r.font.size = Pt(10)
            elif kind == "table":
                rows = payload
                if rows:
                    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
                    t.style = "Table Grid"
                    for i, row in enumerate(rows):
                        for j, cell in enumerate(row):
                            if j < len(t.rows[i].cells):
                                t.rows[i].cells[j].text = cell.replace("`", "")
                    doc.add_paragraph()

        doc.save(str(docx_path))
        return True
    except Exception as e:
        print(f"❌ Ошибка рендера docx: {e}")
        return False


def render_md_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Конвертирует готовый docx в pdf через MS Word (docx2pdf).

    Требует установленный MS Word и пакет docx2pdf.
    Если Word или docx2pdf недоступны — возвращает False.
    """
    if not docx_path.exists():
        print(f"❌ Нет docx для конвертации: {docx_path}")
        return False

    try:
        from docx2pdf import convert
    except ImportError:
        print("⚠️ docx2pdf не установлен: pip install docx2pdf")
        return False

    try:
        convert(str(docx_path), str(pdf_path))
        print(f"✅ PDF (Word): {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ Word не сработал: {e}")
        return False


# ================================================================
# MAIN
# ================================================================
def main() -> None:
    only_missing = "--only-missing" in sys.argv
    MANUALS_DIR.mkdir(parents=True, exist_ok=True)
    created = skipped = 0

    for name, lines in DOCS.items():
        path = MANUALS_DIR / name if name.startswith("USER_MANUAL") else BASE_DIR / name
        existed = path.exists()
        if existed and only_missing:
            print(f"— пропущен (уже есть): {name}")
            skipped += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"✅ {'переписан' if existed else 'создан'}: "
              f"{path.relative_to(BASE_DIR)} ({len(lines)} строк)")
        created += 1

    # ---- USER_MANUAL: .md → .docx + .pdf (прямо в manuals/, без pdf/) ----
    manual_md = MANUALS_DIR / "USER_MANUAL.md"
    if manual_md.exists():
        manual_docx = MANUALS_DIR / "USER_MANUAL.docx"
        manual_pdf = MANUALS_DIR / "USER_MANUAL.pdf"

        print()
        print("📘 Рендерю USER_MANUAL в docx и pdf...")

        if render_md_to_docx(manual_md, manual_docx):
            print(f"✅ DOCX: {manual_docx.relative_to(BASE_DIR)}")
            # PDF только если docx получился
            render_md_to_pdf(manual_docx, manual_pdf)

    print()
    print(f"Готово: создано/переписано {created}, пропущено {skipped}.")
    print("Тексты правятся ТОЛЬКО в словаре DOCS этого файла.")
    print("Бережный режим (не трогать существующее): --only-missing.")


if __name__ == "__main__":
    main()