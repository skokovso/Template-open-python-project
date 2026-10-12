# ЗАПОЛНИТЬ: название проекта

ЗАПОЛНИТЬ: один абзац — что это, зачем, для кого.

## Быстрый старт

```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

Скопируйте `.env.example` в `.env` и заполните значения.

ЗАПОЛНИТЬ: команда запуска и адрес/порт (например `python main.py`).

## Структура

- корень — боевой код (точка входа `main.py` и модули);
- `assets/` — иконки, логотипы, шаблоны для сборки и работы;
- `data/` — данные рантайма (в .gitignore): db, uploads, exports,
  personal, big_files, reports, logs, temp;
- `service/` — служебное: migrations, fixes, deploy, tools, docs;
  запуск ТОЛЬКО через `python service/run.py service/...`;
- `project_info/manuals/` — руководства пользователя (md + docx + pdf);
- `project_info/ai_pack/` — упаковка для ИИ (`service/docs/ai_pack.py`);
- `tests/` — тесты.

## Сборка exe

```
build.bat     # результат: dist\<ProjectName>\<ProjectName>.exe
```

Перед сборкой `build.bat` автоматически генерирует документацию
(включая PDF-инструкцию), собирает exe по `*.spec`.

## Документация

- `ARCHITECTURE.md` — устройство, схема БД, потоки данных.
- `DIGEST.md` — короткий дайджест для быстрого входа в контекст.
- `CHANGELOG.md` — история версий (строка на версию).
- `DEVLOG.md` — журнал сессий разработки (включая неудачные ветки).
- `TODO.md` — открытые задачи.
- `AI_BRIEF.md` — правила и табу для ИИ-ассистентов.
- `QWEN.md` — контекст и правила для AI-ассистента.
- `project_info/manuals/USER_MANUAL.md` — инструкция пользователя (markdown).
- `project_info/manuals/USER_MANUAL.docx` — Word-версия инструкции.
- `project_info/manuals/USER_MANUAL.pdf` — PDF-инструкция (кнопка «?»).

## Генераторы документации

- `service/docs/make_docs.py` — собирает все .md-документы и
  рендерит USER_MANUAL в docx + pdf.
- `service/docs/manuals_to_pdf.py` — fallback md → pdf без Word (fpdf2).
- `service/docs/ai_pack.py` — упаковка проекта для передачи в чат с ИИ.

## Важно

- `data/` (данные рантайма) не коммитится в git.
- `.env` не коммитится, `.env.example` — коммитится как образец.
- Документы проекта генерируются скриптами; правятся только в словаре DOCS.
